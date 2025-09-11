#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2022 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests for utilities used to read and write data externally."""

import os
import sys
import urllib

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.io import open_url


def test_open_url(tmp_path):
    """Checks that the open_url() object reads from a valid URL.

    :param fixture tmp_path: Temp dir.
    """
    f = tmp_path / "open_url.txt"
    f.write_text("abcde")

    request = open_url(f"file://{f}")
    assert request
    assert isinstance(request, urllib.response.addinfourl)
    assert request.read().decode() == 'abcde'
