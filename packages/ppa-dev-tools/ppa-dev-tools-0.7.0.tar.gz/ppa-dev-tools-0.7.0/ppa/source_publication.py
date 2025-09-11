#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2024 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""A package release for a particular distro series."""

from functools import lru_cache

from .lp import Lp
from .constants import URL_AUTOPKGTEST


class SourcePublication:
    """Encapsulate data needed to represent a source publication record.

    This class can be used to hold the data 'coordinates' for a source
    package release, namely the package's name, version, distro series,
    and the archive (PPA) containing it.
    """

    def __init__(self, package, version, series, archive=None, status=None):
        """Initialize a new SourcePublication object for a given SPPH.

        This creates only the local representation of the SPPH, it does
        not cause a new SPPH to be created in or loaded from Launchpad.

        :param str package: The source package name.
        :param str version: The version of the source package to install.
        :param str series: The distro release series codename.
        :param Ppa archive: The Ppa owning this source publication, or
            None if it belongs to the primary archive.
        :param str status: The Launchpad publication state (Pending,
            Published, Superseded, Deleted, Obsolete)
        """
        if not package:
            raise ValueError('undefined package.')
        if not version:
            raise ValueError('undefined version.')
        if not series:
            raise ValueError('undefined series.')

        self.package = package
        self.version = version
        self.series = series
        self.archive = archive
        self.status = status

    def __repr__(self) -> str:
        """Return a machine-parsable unique representation of object.

        :rtype: str
        :returns: Official string representation of the object.
        """
        return (
            f'{self.__class__.__name__}('
            f'package={self.package!r}, '
            f'version={self.version!r}, '
            f'series={self.series!r}, '
            f'archive={self.archive!r}, '
            f'status={self.status!r})'
        )

    def __str__(self) -> str:
        """Return a displayable string identifying the SPPH.

        :rtype: str
        :returns: Human-readable string.
        """
        address = f"{self.series}/{self.package}/{self.version}"
        if self.archive:
            address += f" ({self.archive})"
        if self.status:
            address += f": {self.status}"
        return address

    @lru_cache
    def to_dict(self) -> dict:
        """Return a basic dict structure of the SourcePublication's data."""
        return {
            'package': self.package,
            'version': self.version,
            'series': self.series,
            'archive': self.archive,
            'status': self.status
        }

    @property
    @lru_cache
    def autopkgtest_history_url(self) -> str:
        """Renders the SPPH as a URL to the autopkgtest history.

        :rtype: str
        :returns: Autopkgtest history URL.
        """
        if self.package.startswith('lib'):
            prefix = self.package[0:4]
        else:
            prefix = self.package[0]
        pkg_str = f"{prefix}/{self.package}"
        return f"{URL_AUTOPKGTEST}/packages/{pkg_str}/{self.series}"


if __name__ == "__main__":
    print('##################################')
    print('## Publication class smoke test ##')
    print('##################################')
    print()

    lp = Lp('smoketest', staging=True)
    pub = SourcePublication('p', '1.0', 'noble', None, 'Published')
    print(repr(pub))
    print()
    print(str(pub))
    print()
    print(pub.to_dict())
    print()
    print(pub.autopkgtest_history_url)
