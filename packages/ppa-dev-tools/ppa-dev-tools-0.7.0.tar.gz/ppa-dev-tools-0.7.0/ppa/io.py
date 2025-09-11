#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Copyright (C) 2022 Authors
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.
#
# Authors:
#   Bryce Harrington <bryce@canonical.com>

"""Utilities for reading input and writing output to external locations."""

import sys
import urllib.request


def open_url(url, desc="data"):
    """Open a remote URL for reading.

    :rtype: urllib.request.Request
    :returns: A request object for the stream to read from, or None on error.
    """
    request = urllib.request.Request(url)
    request.add_header('Cache-Control', 'max-age=0')
    try:
        return urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            # 401 means access denied.  Launchpad sometimes returns this
            # when something is not published yet.
            return None
        elif e.code == 404:
            # 404 means not found; prefer not to emit error messages
            return None
        else:
            sys.stderr.write(f"Error: Could not retrieve {desc} from {url}: {e}\n")
            return None
