#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Fri Jan 05 2024 18:10:01 by codeskyblue
"""
import logging

from packaging.version import Version
from pymobiledevice3.common import get_home_folder
from pymobiledevice3.exceptions import AlreadyMountedError
from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.amfi import AmfiService
from pymobiledevice3.services.mobile_image_mounter import auto_mount

from tidevice3.cli.cli_common import cli, pass_service_provider

logger = logging.getLogger(__name__)


@cli.command(name="developer")
@pass_service_provider
def cli_developer(service_provider: LockdownClient):
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
    