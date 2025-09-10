#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Fri Jan 05 2024 18:10:01 by codeskyblue
"""
from __future__ import annotations

import click
from pymobiledevice3.cli.cli_common import print_json

from tidevice3.api import list_devices
from tidevice3.cli.cli_common import cli
from tidevice3.utils.common import print_dict_as_table


@cli.command(name="list")
@click.option("-u", "--usb", is_flag=True, help="show only USB devices")
@click.option("-n", "--network", is_flag=True, help="show only network devices")
@click.option("--json", is_flag=True, help="output as json format")
@click.option("--color/--no-color", default=True, help="print colored output")
@click.option("--timeout", default=5.0, type=float, help="timeout for device connection in seconds (default: 5.0)")
@click.option("-v", "--verbose", is_flag=True, help="show detailed connection process")
@click.pass_context
def cli_list(ctx: click.Context, usb: bool, network: bool, json: bool, color: bool, timeout: float, verbose: bool):
    """List connected devices
    
    Examples:
        t3 list                    # List all devices (default timeout: 5s)
        t3 list --usb              # List only USB devices
        t3 list --network          # List only network devices  
        t3 list --timeout 10       # Use 10s timeout
        t3 list --verbose          # Show connection progress
        t3 list --json             # Output as JSON
    """
    import logging
    
    # Set log level based on verbose flag
    if verbose:
        logging.getLogger('tidevice3.api').setLevel(logging.INFO)
    else:
        logging.getLogger('tidevice3.api').setLevel(logging.WARNING)
    
    usbmux_address = ctx.obj["usbmux_address"]
    
    # Validate parameters
    if timeout <= 0:
        click.echo("Error: timeout must be greater than 0", err=True)
        ctx.exit(1)
    
    if verbose:
        click.echo(f"🔍 Searching for devices (timeout: {timeout}s)...")
    
    devices = list_devices(usb, network, usbmux_address, timeout)
    
    if not devices:
        if verbose:
            click.echo("❌ No devices found")
        ctx.exit(0)
    
    if json:
        print_json([d.model_dump() for d in devices], color)
    else:
        if verbose:
            click.echo(f"✅ Found {len(devices)} connected device(s):")
        headers = ["Identifier", "DeviceName", "ProductType", "ProductVersion", "ConnectionType"]
        print_dict_as_table([d.model_dump() for d in devices], headers)


