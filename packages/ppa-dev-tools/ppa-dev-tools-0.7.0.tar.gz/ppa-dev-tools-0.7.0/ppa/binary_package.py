#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Copyright (C) 2023 Authors
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.
#
# Authors:
#   Bryce Harrington <bryce@canonical.com>

"""Interprets and analyzes an Ubuntu Apt record for a binary package."""

from functools import lru_cache
from typing import Dict

from .dict import unpack_to_dict


class BinaryPackage:
    """The Apt record about an installable binary .deb.

    SourcePackages are built into multiple BinaryPackages for different
    components and different architectures.

    This object is intended to be instantiated from a raw Apt binary
    package record such as extracted from a Packages.xz file by
    apt_pkg.TagFile().  The BinaryPackage class members handle the
    parsing and interpretation of the data values of the record such as
    installation dependencies.

    Since objects of this class are constructed as thin wrappers on the
    Apt record, the available member properties for the object will vary
    depending on the data elements present in the record.  For example,
    if there isn't a "Task:" field, then this object will not have a
    'self.task' property.

    For member properties needed by users of this class, it's
    recommended to guarantee their presence either by requiring them
    from the pkg_dict in the __init__() property, or add a property to
    the class that checks and substitutes a suitable default if missing.
    """
    # pylint: disable=no-member

    def __init__(self, pkg_dict: dict):
        """Initialize a new SourcePackage object for a given package.

        :param dict[str, str] pkg_dict: Data collection loaded from an Apt record.
        """
        # Auto-create member parameters from the Apt record's data structure
        for k, val in dict(pkg_dict).items():
            setattr(self, k.lower().replace('-', '_'), val)

        # Required fields that must be present in pkg_dict for object validity
        for field in ['package', 'version', 'architecture']:
            if getattr(self, field, None) is None:
                raise ValueError(f'undefined {field} from Apt record for binary package')

    def __repr__(self):
        """Return a machine-parsable unique representation of object.

        :rtype: str
        :returns: Official string representation of the object.
        """
        return (f'{self.__class__.__name__}('
                f'pkg_dict={vars(self)!r})')

    def __str__(self):
        """Return a human-readable textual description of the BinaryPackage.

        :rtype: str
        :returns: Human-readable string.
        """
        return f"{self.package} ({self.version}) [{self.architecture}]"

    @property
    def name(self):
        """The name of the binary package as recorded in the Apt database.

        :rtype: str
        :returns: Package name.
        """
        return self.package

    @property
    @lru_cache
    def installation_dependencies(self) -> Dict[str, str]:
        """Required binary packages that must be installed as prerequisites.

        :rtype: dict[str, str]
        :returns: Collection of package names to version specification strings.
        """
        if getattr(self, 'depends', None) is None:
            # Missing Depends is uncommon, but can occur for packages
            # consisting just of config files, for example.
            return {}
        deps = unpack_to_dict(self.depends, key_sep=' ')
        if not deps:
            raise RuntimeError('Could not parse packages from Depends line of Apt record.')
        return deps

    @property
    @lru_cache
    def recommended_packages(self) -> Dict[str, str]:
        """Optional binary packages intended to be co-installed.

        :rtype: dict[str, str]
        :returns: Collection of package names to version specification strings.
        """
        if getattr(self, 'recommends', None) is None:
            return {}
        recs = unpack_to_dict(self.recommends, key_sep=' ')
        if not recs:
            raise RuntimeError('Could not parse packages from Recommends line of Apt record.')
        return recs


if __name__ == "__main__":
    # pylint: disable=line-too-long, invalid-name

    import os
    import apt_pkg

    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    root_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
    tests_data_dir = os.path.join(root_dir, 'tests', 'data')
    assert os.path.exists(tests_data_dir), f'cannot find {tests_data_dir}'

    print('####################################')
    print('## BinaryPackage class smoke test ##')
    print('####################################')
    print()

    print('Binary Packages')
    print('---------------')
    with apt_pkg.TagFile(f'{tests_data_dir}/binary-amd64/Packages.xz') as pkgs:
        results = []
        for pkg in pkgs:
            binary = BinaryPackage(pkg)
            results.append(str(binary))

        num_results = len(results)
        ellipses_shown = False
        for i, result in enumerate(results):
            if i < 10 or i >= num_results - 10:
                print(result)
            elif not ellipses_shown:
                print('...')
                ellipses_shown = True
    print()

    print('Details for "dovecot-core"')
    print('--------------------------')
    package_data = {
        'Package': 'dovecot-core',
        'Architecture': 'amd64',
        'Version': '1:2.3.19.1+dfsg1-2ubuntu4',
        'Priority': 'optional',
        'Section': 'mail',
        'Source': 'dovecot',
        'Origin': 'Ubuntu',
        'Maintainer': 'Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>',
        'Original-Maintainer': 'Dovecot Maintainers <dovecot@packages.debian.org>',
        'Bugs': 'https://bugs.launchpad.net/ubuntu/+filebug',
        'Installed-Size': '10406',
        'Provides': 'dovecot-abi-2.3.abiv19, dovecot-common',
        'Pre-Depends': 'init-system-helpers (>= 1.54~)',
        'Depends': 'adduser, libpam-runtime, lsb-base, openssl, ssl-cert, ucf, libapparmor1 (>= 2.7.0~beta1+bzr1772), libbz2-1.0, libc6 (>= 2.36), libcap2 (>= 1:2.10), libcrypt1 (>= 1:4.1.0), libexttextcat-2.0-0 (>= 3.3.0), libicu72 (>= 72.1~rc-1~), liblua5.3-0, liblz4-1 (>= 0.0~r130), liblzma5 (>= 5.1.1alpha+20120614), libpam0g (>= 0.99.7.1), libsodium23 (>= 1.0.13), libssl3 (>= 3.0.0), libstemmer0d (>= 0+svn527), libsystemd0, libtirpc3 (>= 1.0.2), libunwind8, libwrap0 (>= 7.6-4~), libzstd1 (>= 1.5.2), zlib1g (>= 1:1.1.4)',  # noqa: E501
        'Suggests': 'dovecot-gssapi, dovecot-imapd, dovecot-ldap, dovecot-lmtpd, dovecot-lucene, dovecot-managesieved, dovecot-mysql, dovecot-pgsql, dovecot-pop3d, dovecot-sieve, dovecot-solr, dovecot-sqlite, dovecot-submissiond, ntp',  # noqa: E501
        'Breaks': 'dovecot-common (<< 1:2.0.14-2~), mailavenger (<< 0.8.1-4)',
        'Replaces': 'dovecot-common (<< 1:2.0.14-2~), mailavenger (<< 0.8.1-4)',
        'Filename': 'pool/main/d/dovecot/dovecot-core_2.3.19.1+dfsg1-2ubuntu4_amd64.deb',
        'Size': '3300962',
        'MD5sum': 'c6f61ffe0f01f51405c4fc22f6770cd2',
        'SHA1': 'ed389250d8738c0199f24cab2fe33e12b84e31c7',
        'SHA256': 'd73fb4bc55c764b9ad8c143c1f2b04a1cfb6ce2c2d751e4970ee09199ed7c3cb',
        'SHA512': 'ab55bdcdc31eac59168883ff83b2e6f2ee57b9340eb6b4e5b0f4e354813ae7dc0ca21ba34265f872a9c014b3c06bacad95708059c7a06c8c93d4a22ccb31494c',  # noqa: E501
        'Homepage': 'https://dovecot.org/',
        'Description': 'secure POP3/IMAP server - core files',
        'Task': 'mail-server',
        'Description-md5': '42825422b1ef9e3a592c94dfafed375c',
    }

    binary = BinaryPackage(package_data)

    print('* Object:')
    pp.pprint(vars(binary))

    print()
    print('* Installation Requires:')
    for pkg, ver in sorted(binary.installation_dependencies.items()):
        print(f'  - {pkg}: {ver}')

    print()
    print('* Recommends:')
    for pkg, ver in sorted(binary.recommended_packages.items()):
        print(f'  - {pkg}: {ver} ')
