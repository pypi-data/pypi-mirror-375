#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2019 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests the package's version tracking module.

Note this is for PpaDevTool's own versioning system.  This is unrelated
to Ubuntu or Debian version numbering.
"""

import os
import sys

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa._version import __version__, __version_info__


def test_version():
    """Checks that the __version__ is specified correctly."""
    assert type(__version__) is str
    assert '.' in __version__
    assert __version__[0].isdigit()
    assert __version__[-1] != '.'


def test_version_info():
    """Checks that the __version_info__ is specified correctly."""
    assert type(__version_info__) is tuple
    assert len(__version_info__) > 1
    for elem in __version_info__:
        assert type(elem) is int
        assert elem >= 0
