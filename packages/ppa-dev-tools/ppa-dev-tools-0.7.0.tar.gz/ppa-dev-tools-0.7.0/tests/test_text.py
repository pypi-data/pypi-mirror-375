#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2022 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests the text helper routines."""

import os
import sys

import pytest

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

import ppa.text


@pytest.mark.parametrize('input, expected', [
    ('true', True),
    ('t', True),
    ('yes', True),
    ('y', True),
    ('1', True),
    ('false', False),
    ('f', False),
    ('no', False),
    ('n', False),
    ('0', False),
    ('', False),
    (1, True),
    (0, False),
    (1.0, True),
    (0.0, False),
    ((), False),
    ((1,), True),
    (None, False),
    (object(), True),
])
def test_to_bool(input, expected):
    """Check that the given input produces the expected true/false result.

    :param * input: Any available type to be converted to boolean.
    :param bool expected: The True or False result to expect.
    """
    assert ppa.text.to_bool(input) == expected


def test_ansi_hyperlink():
    """Check that text can be linked with a url."""
    assert ppa.text.ansi_hyperlink("xxx", "yyy") == "\u001b]8;;xxx\u001b\\yyy\u001b]8;;\u001b\\"
