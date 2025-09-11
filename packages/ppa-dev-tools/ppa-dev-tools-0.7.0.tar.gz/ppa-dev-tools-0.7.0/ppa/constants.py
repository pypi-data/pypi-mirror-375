#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Copyright (C) 2022 Authors
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.
#
# Authors:
#   Bryce Harrington <bryce@canonical.com>

"""Global constants."""

ARCHES_ALL = ["amd64", "arm64", "armhf", "armel", "i386", "powerpc", "ppc64el", "s390x", "riscv64"]
ARCHES_PPA_DEFAULT = ["amd64", "i386"]
ARCHES_PPA_ALL = ["amd64", "arm64", "armhf", "i386", "ppc64el", "s390x", "riscv64"]
ARCHES_PPA_EXTRA = []
ARCHES_PPA_LEGACY = list(set(ARCHES_ALL) - set(ARCHES_PPA_ALL + ARCHES_PPA_EXTRA))

ARCHES_AUTOPKGTEST = ["amd64", "arm64", "armhf", "i386", "ppc64el", "s390x", "riscv64"]

CREDENTIALS_FILENAME_DEFAULT = "credentials.oauth"

URL_LPAPI = "https://api.launchpad.net/devel"
URL_AUTOPKGTEST = "https://autopkgtest.ubuntu.com"

DISTRO_UBUNTU_COMPONENTS = ['main', 'restricted', 'universe', 'multiverse', 'partner']

DISTRO_UBUNTU_POCKETS = ['release', 'security', 'proposed', 'updates', 'backports']
DISTRO_UBUNTU_POCKETS_UPDATES = ['release', 'security', 'updates']

LOCAL_REPOSITORY_PATH = "/tmp/ubuntu"
LOCAL_REPOSITORY_MIRRORING_DIRECTIONS = f"""
Tip: You can generate (and refresh) a dists-only mirror thusly:
  $ mkdir {LOCAL_REPOSITORY_PATH}
  $ rsync -va \\
      --exclude={{'*/installer*','*/i18n/*','*/uefi/*','*/Contents*','*/by-hash/*','*tar.gz'}} \\
      rsync://archive.ubuntu.com/ubuntu/dists {LOCAL_REPOSITORY_PATH}

It's recommended to run the rsync command as a cronjob to keep your
repository up to date as often as desired.
"""
