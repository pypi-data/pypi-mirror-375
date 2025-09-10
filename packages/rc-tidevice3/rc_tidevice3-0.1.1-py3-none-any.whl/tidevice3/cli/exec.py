#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Mon Jan 15 2024 18:54:35 by codeskyblue
"""

from __future__ import annotations

import os
import sys

import click

from tidevice3.cli.cli_common import cli


@cli.command(name="exec", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
@click.pass_context
def _exec(ctx: click.Context, args: list[str]):
    """ translate to pymobiledevice3 command, eg: t3 exec version """
    args = [sys.executable, '-m', 'pymobiledevice3'] + list(args)
    if ctx.obj['udid']:
        args += ['--udid', ctx.obj['udid']]
    os.execv(args[0], args)
