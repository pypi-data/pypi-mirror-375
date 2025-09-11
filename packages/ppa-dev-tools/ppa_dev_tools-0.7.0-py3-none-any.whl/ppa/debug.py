#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2019 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

import sys
import pprint
import textwrap

DEBUGGING = False


def dbg(msg, wrap=0, prefix=None, indent=''):
    """Print information if debugging is enabled."""
    if DEBUGGING:
        if type(msg) is str:
            if wrap == 0 and indent != '':
                wrap = 72
            if wrap > 0:
                if prefix is None and len(indent) > 0:
                    prefix = indent
                msg = textwrap.fill(
                    msg,
                    width=wrap,
                    initial_indent=prefix,
                    subsequent_indent=indent)
            sys.stderr.write(f"{msg}\n")
        else:
            pprint.pprint(msg)


def warn(msg):
    """Print warning message to stderr."""
    sys.stderr.write(f"Warning: {msg}\n")


def error(msg):
    """Print error message to stderr."""
    sys.stderr.write(f"Error: {msg}\n")
