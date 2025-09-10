
from __future__ import annotations

import datetime
import io
import logging
import os
import signal
import socket
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from typing import Any, Dict, Iterator, Optional

import requests
from packaging.version import Version
from PIL import Image
from pydantic import BaseModel
from pymobiledevice3.common import get_home_folder
from pymobiledevice3.exceptions import AlreadyMountedError
from pymobiledevice3.lockdown import LockdownClient, create_using_usbmux, usbmux
from pymobiledevice3.lockdown_service_provider import LockdownServiceProvider
from pymobiledevice3.remote.remote_service_discovery import RemoteServiceDiscoveryService
from pymobiledevice3.services.amfi import AmfiService
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.services.dvt.instruments.device_info import DeviceInfo
from pymobiledevice3.services.dvt.instruments.screenshot import Screenshot
from pymobiledevice3.services.installation_proxy import InstallationProxyService
from pymobiledevice3.services.mobile_image_mounter import auto_mount
from pymobiledevice3.services.screenshot import ScreenshotService
from pymobiledevice3.utils import get_asyncio_loop

from tidevice3.exceptions import FatalError
from tidevice3.utils.download import download_file, is_hyperlink

logger = logging.getLogger(__name__)

class DeviceShortInfo(BaseModel):
    BuildVersion: str
    ConnectionType: Optional[str]
    DeviceClass: str
    DeviceName: str
    Identifier: str
    ProductType: str
    ProductVersion: str


class ProcessInfo(BaseModel):
    isApplication: bool
    pid: int
    name: str
    realAppName: str
    startDate: datetime.datetime
    bundleIdentifier: Optional[str] = None
    foregroundRunning: Optional[bool] = None


def _connect_to_device(device, usbmux_address: Optional[str] = None, timeout: float = 5.0) -> Optional[DeviceShortInfo]:
    """Helper function to connect to a single device with error handling"""
    udid = device.serial
    
    # Set socket timeout to prevent hanging
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    
    try:
        lockdown = create_using_usbmux(
            udid,
            autopair=False,
            connection_type=device.connection_type,
            usbmux_address=usbmux_address,
        )
        info = DeviceShortInfo.model_validate(lockdown.short_info)
        logger.debug(f"Successfully connected to device {udid}")
        return info
    except Exception as e:
        logger.warning(f"Failed to connect to device {udid}: {e}")
        return None
    finally:
        # Restore original socket timeout
        socket.setdefaulttimeout(original_timeout)


def list_devices(
    usb: bool = True, network: bool = False, usbmux_address: Optional[str] = None, timeout: float = 5.0
) -> list[DeviceShortInfo]:
    """List connected devices with timeout for each device connection"""
    devices = usbmux.list_devices(usbmux_address=usbmux_address)
    
    # Filter devices based on connection type - simplified logic
    if not usb and not network:
        # If both are False, show all devices
        filtered_devices = devices
    else:
        filtered_devices = [
            device for device in devices
            if (usb and device.is_usb) or (network and device.is_network)
        ]
    
    if not filtered_devices:
        logger.info("No devices found matching the criteria")
        return []
    
    logger.info(f"Found {len(filtered_devices)} devices, checking connectivity...")
    connected_devices = []
    
    # Use ThreadPoolExecutor to process devices with timeout
    max_workers = min(len(filtered_devices), 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all device connection tasks
        future_to_device = {
            executor.submit(_connect_to_device, device, usbmux_address, timeout): device 
            for device in filtered_devices
        }
        
        # Process completed tasks with overall timeout
        completed_count = 0
        overall_timeout = timeout * len(filtered_devices) + 5  # 5 seconds buffer
        
        try:
            for future in as_completed(future_to_device, timeout=overall_timeout):
                device = future_to_device[future]
                udid = device.serial
                completed_count += 1
                
                try:
                    # Individual timeout for each device
                    result = future.result(timeout=0.1)  # Very short timeout since it should be done
                    if result is not None:
                        connected_devices.append(result)
                        logger.debug(f"Device {udid} connected successfully ({completed_count}/{len(filtered_devices)})")
                    else:
                        logger.debug(f"Device {udid} connection failed ({completed_count}/{len(filtered_devices)})")
                except TimeoutError:
                    logger.warning(f"Timeout connecting to device {udid} after {timeout}s ({completed_count}/{len(filtered_devices)})")
                except Exception as e:
                    logger.warning(f"Unexpected error with device {udid}: {e} ({completed_count}/{len(filtered_devices)})")
        except TimeoutError:
            # Overall timeout reached - cancel remaining futures
            logger.warning(f"Overall timeout ({overall_timeout}s) reached, cancelling remaining connections")
            for future in future_to_device:
                if not future.done():
                    future.cancel()
                    device = future_to_device[future]
                    logger.warning(f"Cancelled connection to device {device.serial}")
    
    logger.info(f"Successfully connected to {len(connected_devices)}/{len(filtered_devices)} devices")
    return connected_devices


DEFAULT_TIMEOUT = 60

def connect_service_provider(udid: Optional[str], force_usbmux: bool = False, usbmux_address: Optional[str] = None) -> LockdownServiceProvider:
    """Connect to device and return LockdownServiceProvider"""
    lockdown = create_using_usbmux(serial=udid, usbmux_address=usbmux_address)
    if force_usbmux:
        return lockdown
    if lockdown.product_version >= "17":
        return connect_remote_service_discovery_service(lockdown.udid)
    return lockdown


class EnterableRemoteServiceDiscoveryService(RemoteServiceDiscoveryService):
    def __enter__(self) -> EnterableRemoteServiceDiscoveryService:
        get_asyncio_loop().run_until_complete(self.connect())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        get_asyncio_loop().run_until_complete(self.close())


def is_port_open(ip: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((ip, port)) == 0


def connect_remote_service_discovery_service(udid: str, tunneld_url: str = None) -> EnterableRemoteServiceDiscoveryService:
    if tunneld_url is None:
        if is_port_open("localhost", 49151):
            tunneld_url = "http://localhost:49151"
        else:
            tunneld_url = "http://localhost:5555" # for backward compatibility

    try:
        resp = requests.get(tunneld_url, timeout=DEFAULT_TIMEOUT)
        tunnels: Dict[str, Any] = resp.json()
        ipv6_address = tunnels.get(udid)
        if ipv6_address is None:
            raise FatalError("tunneld not ready for device", udid)
        rsd = EnterableRemoteServiceDiscoveryService(ipv6_address)
        return rsd
    except requests.RequestException:
        raise FatalError("Please run `sudo t3 tunneld` first")
    except (TimeoutError, ConnectionError):
        raise FatalError("RemoteServiceDiscoveryService connect failed")

def iter_screenshot(service_provider: LockdownClient) -> Iterator[bytes]:
    if int(service_provider.product_version.split(".")[0]) >= 17:
        with DvtSecureSocketProxyService(lockdown=service_provider) as dvt:
            screenshot_service = Screenshot(dvt)
            while True:
                yield screenshot_service.get_screenshot()
    else:
        screenshot_service = ScreenshotService(service_provider)
        while True:
            yield screenshot_service.take_screenshot()


def screenshot_png(service_provider: LockdownClient) -> bytes:
    """ get screenshot as png data """
    it = iter_screenshot(service_provider)
    png_data = next(it)
    it.close()
    return png_data


def screenshot(service_provider: LockdownClient) -> Image.Image:
    """ get screenshot as PIL.Image.Image """
    png_data = screenshot_png(service_provider)
    return Image.open(io.BytesIO(png_data)).convert("RGB")


def proclist(service_provider: LockdownClient) -> Iterator[ProcessInfo]:
    """ list running processes"""
    with DvtSecureSocketProxyService(lockdown=service_provider) as dvt:
        processes = DeviceInfo(dvt).proclist()
        for process in processes:
            if 'startDate' in process:
                process['startDate'] = str(process['startDate'])
                yield ProcessInfo.model_validate(process)


def app_install(service_provider: LockdownClient, path_or_url: str):
    if is_hyperlink(path_or_url):
        ipa_path = download_file(path_or_url)
    elif os.path.isfile(path_or_url):
        ipa_path = path_or_url
    else:
        raise ValueError("local file not found", path_or_url)
    InstallationProxyService(lockdown=service_provider).install_from_local(ipa_path)


def enable_developer_mode(service_provider: LockdownClient):
    """ enable developer mode """
    if Version(service_provider.product_version) >= Version("16"):
        if not service_provider.developer_mode_status:
            logger.info('enable developer mode')
            AmfiService(service_provider).enable_developer_mode()
        else:
            logger.info('developer mode already enabled')
    
    try:
        xcode = get_home_folder() / 'Xcode.app'
        xcode.mkdir(parents=True, exist_ok=True)
        auto_mount(service_provider, xcode=xcode)
        logger.info('mount developer image')
    except AlreadyMountedError:
        logger.info('developer image already mounted')
        