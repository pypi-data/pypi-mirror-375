#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Copyright (C) 2023 Authors
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.
#
# Authors:
#   Bryce Harrington <bryce@canonical.com>

"""Interprets and analyzes an Ubuntu Apt record for a source package."""

from functools import lru_cache
from typing import Dict

from .dict import unpack_to_dict


class SourcePackage:
    """The Apt record for the packaged source of a software codebase.

    This object is intended to be instantiated from a raw Apt source
    package record such as extracted from a Sources.xz file by
    apt_pkg.TagFile().  The SourcePackage class members handle the
    parsing and interpretation of the data values of the record such as
    build dependencies.

    Since objects of this class are constructed as thin wrappers on the
    Apt record, the available member properties for the object will vary
    depending on the data elements present in the record.  For example,
    if there isn't a "Testsuite:" field, then this object will not have a
    'self.testsuite' property.

    For member properties needed by users of this class, it's
    recommended to guarantee their presence either by requiring them
    from the pkg_dict in the __init__() property, or add a property to
    the class that checks and substitutes a suitable default if missing.
    """
    # pylint: disable=no-member

    def __init__(self, pkg_dict: dict):
        """Initialize a new SourcePackage object for a given package.

        :param dict[str, str] pkg_dict: Data collection loaded from am Apt record.
        """
        # Auto-create member parameters from the Apt record's data structure
        for k, val in dict(pkg_dict).items():
            setattr(self, k.lower().replace('-', '_'), val)

        for field in ['package', 'version', 'binary']:
            if getattr(self, field, None) is None:
                raise ValueError(f'undefined {field} from Apt record for source package')

    def __repr__(self):
        """Return a machine-parsable unique representation of object.

        :rtype: str
        :returns: Official string representation of the object.
        """
        return (f'{self.__class__.__name__}('
                f'pkg_dict={vars(self)!r})')

    def __str__(self) -> str:
        """Return a human-readable textual description of the SourcePackage.

        :rtype: str
        :returns: Human-readable string.
        """
        return f"{self.package} ({self.version})"

    @property
    def name(self) -> str:
        """The name of the source package as recorded in the Apt database.

        :rtype: str
        :returns: Package name.
        """
        return self.package

    @property
    @lru_cache
    def provides_binaries(self) -> Dict[str, str]:
        """The binary package names provided by this source package.

        For consistency, the results are provided as a dict structure,
        however since the Binary field is a simple comma-separated list,
        the dict will only have keys, with no defined values.

        :rtype: dict[str, str]
        :returns: Collection of binary packages this source provides.
        """
        bins = unpack_to_dict(self.binary)
        if not bins:
            raise RuntimeError('Could not parse packages from Binaries line of Apt record.')
        return bins

    @property
    @lru_cache
    def build_dependencies(self) -> Dict[str, str]:
        """The binary packages that must be available to build this source package.

        :rtype: dict[str, BinaryPackages]
        :returns: Collection of package names to version specification strings.
        """
        if getattr(self, 'build_depends', None) is None:
            # Missing BuildDepends is uncommon, but can occur for packages
            # consisting just of config files, for example.
            return {}
        deps = unpack_to_dict(self.build_depends, key_sep=' ')
        if not deps:
            raise RuntimeError('Could not parse packages from Build-Depends line of Apt record.')
        return deps


if __name__ == "__main__":
    # pylint: disable=line-too-long, invalid-name

    import os
    import apt_pkg

    from pprint import PrettyPrinter
    pp = PrettyPrinter(indent=4)

    root_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
    tests_data_dir = os.path.join(root_dir, 'tests', 'data')
    assert os.path.exists(tests_data_dir), f'cannot find {tests_data_dir}'

    print('####################################')
    print('## SourcePackage class smoke test ##')
    print('####################################')

    print()
    print('Source Packages')
    print('---------------')
    with apt_pkg.TagFile(f'{tests_data_dir}/source/Sources.xz') as pkgs:
        results = []
        for pkg in pkgs:
            source = SourcePackage(pkg)
            results.append(str(source))

        num_results = len(results)
        ellipses_shown = False
        for i, result in enumerate(results):
            if i < 10 or i >= num_results - 10:
                print(result)
            elif not ellipses_shown:
                print('...')
                ellipses_shown = True
    print()

    print()
    print('Details for "dovecot"')
    print('---------------------')
    package_data = {
        'Package': 'dovecot',
        'Format': '3.0 (quilt)',
        'Binary': 'dovecot-core, dovecot-dev, dovecot-imapd, dovecot-pop3d, dovecot-lmtpd, dovecot-managesieved, dovecot-pgsql, dovecot-mysql, dovecot-sqlite, dovecot-ldap, dovecot-gssapi, dovecot-sieve, dovecot-solr, dovecot-lucene, dovecot-submissiond, dovecot-auth-lua',  # noqa: E501
        'Architecture': 'any',
        'Version': '1:2.3.19.1+dfsg1-2ubuntu4',
        'Priority': 'optional',
        'Section': 'mail',
        'Maintainer': 'Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>',
        'Original-Maintainer': 'Dovecot Maintainers <dovecot@packages.debian.org>',
        'Uploaders': 'Jaldhar H. Vyas <jaldhar@debian.org>, Jelmer Vernooij <jelmer@debian.org>, Apollon Oikonomopoulos <apoikos@debian.org>, Noah Meyerhans <noahm@debian.org>',  # noqa: E501
        'Standards-Version': '4.6.1',
        'Build-Depends': 'debhelper-compat (= 13), default-libmysqlclient-dev, krb5-multidev, libapparmor-dev [linux-any], libbz2-dev, libcap-dev [linux-any], libclucene-dev, libdb-dev, libexpat-dev, libexttextcat-dev, libicu-dev, libldap2-dev, liblua5.3-dev, liblz4-dev, liblzma-dev, libpam0g-dev, libpq-dev, libsasl2-dev, libsodium-dev, libsqlite3-dev, libssl-dev, libstemmer-dev, libsystemd-dev [linux-any], libunwind-dev [amd64 arm64 armel armhf hppa i386 ia64 mips mips64 mips64el mipsel powerpc powerpcspe ppc64 ppc64el sh4], libwrap0-dev, libzstd-dev, lsb-release, pkg-config, zlib1g-dev',  # noqa: E501
        'Testsuite': 'autopkgtest',
        'Homepage': 'https://dovecot.org/',
        'Vcs-Browser': 'https://salsa.debian.org/debian/dovecot',
        'Vcs-Git': 'https://salsa.debian.org/debian/dovecot.git',
        'Directory': 'pool/main/d/dovecot',
        'Package-List': """
         dovecot-auth-lua deb mail optional arch=any
         dovecot-core deb mail optional arch=any
         dovecot-dev deb mail optional arch=any
         dovecot-gssapi deb mail optional arch=any
         dovecot-imapd deb mail optional arch=any
         dovecot-ldap deb mail optional arch=any
         dovecot-lmtpd deb mail optional arch=any
         dovecot-lucene deb mail optional arch=any
         dovecot-managesieved deb mail optional arch=any
         dovecot-mysql deb mail optional arch=any
         dovecot-pgsql deb mail optional arch=any
         dovecot-pop3d deb mail optional arch=any
         dovecot-sieve deb mail optional arch=any
         dovecot-solr deb mail optional arch=any
         dovecot-sqlite deb mail optional arch=any
         dovecot-submissiond deb mail optional arch=any
         """,  # noqa: E501
        'Files': """
         146ac1a3b2a90d96b7fe8c458a561ae2 3977 dovecot_2.3.19.1+dfsg1-2ubuntu4.dsc
         f8c84c45b05352d55c3dbd509389cc25 1636590 dovecot_2.3.19.1+dfsg1.orig-pigeonhole.tar.gz
         c334e8ef30546af8a668437f046f3f15 7790851 dovecot_2.3.19.1+dfsg1.orig.tar.gz
         c3e7d443a8f4854897d338a56f85c936 67620 dovecot_2.3.19.1+dfsg1-2ubuntu4.debian.tar.xz
         """,  # noqa: E501
        'Checksums-Sha1': """
         481053992c60990f765e0f671e6fc08e910a50b7 3977 dovecot_2.3.19.1+dfsg1-2ubuntu4.dsc
         cdf68b407f1237e92987c6353c9596f3458e2126 1636590 dovecot_2.3.19.1+dfsg1.orig-pigeonhole.tar.gz
         a35f87db78847ba469d9b0e3b72f15f8c5d1d9b0 7790851 dovecot_2.3.19.1+dfsg1.orig.tar.gz
         b50aac6b2aac52744e7ef459030bfefd15cedc71 67620 dovecot_2.3.19.1+dfsg1-2ubuntu4.debian.tar.xz
         """,  # noqa: E501
        'Checksums-Sha256': """
         560f603209443dc92f5941dc1a5b737e3a743defc45d56a1a48df3846deed0f8 3977 dovecot_2.3.19.1+dfsg1-2ubuntu4.dsc
         9bc08c0eeefd75452033e022936968ff0ddad037672effdffc4a7c8dd360b8e0 1636590 dovecot_2.3.19.1+dfsg1.orig-pigeonhole.tar.gz
         db5abcd87d7309659ea6b45b2cb6ee9c5f97486b2b719a5dd05a759e1f6a5c51 7790851 dovecot_2.3.19.1+dfsg1.orig.tar.gz
         7477feb66c8b8b4bab6fa4aadaab8675d308d575e5af662769e179a4fd6e289f 67620 dovecot_2.3.19.1+dfsg1-2ubuntu4.debian.tar.xz
         """,  # noqa: E501
        'Checksums-Sha512': """
         26ab2a3b3a29ee0734ffccbad826b68b8b290715b0dbebdc07e87bac66c5be07cb0bc303c8795fb9dab8c90c9802887ac7c2ddff4b4d789bbc61080a47379e1b 3977 dovecot_2.3.19.1+dfsg1-2ubuntu4.dsc
         a3d1ebab2896954d159af11df3de3993493ae304343fa41d7f408427f8bd19b3061a09017cfe2b62145b4aacaed87b1d9718418b3c73ae9ea700865844e5af39 1636590 dovecot_2.3.19.1+dfsg1.orig-pigeonhole.tar.gz
         ceb87a5f76b6352d28fd030aae5ad2165a133e9a8a6309891e793911203fc0ada9fb254dc05d183eaaa7e2b9851d3f1755b33f08fa6ff5b4b415ac4272bfe150 7790851 dovecot_2.3.19.1+dfsg1.orig.tar.gz
         2e5f62cb3d9685b57f76dbdf81edd2de6df7063ce96d39e75241ee63ab522acd7c7be932ed5d6ed898e5d6e179dd7e226e011226fd3b4271af562af8fe56ec89 67620 dovecot_2.3.19.1+dfsg1-2ubuntu4.debian.tar.xz
         """,  # noqa: E501
        'Testsuite-Triggers': 'lsb-release, python3, systemd-sysv',
        }

    source = SourcePackage(package_data)

    print('* Object:')
    pp.pprint(vars(source))

    print()
    print('* Provides Binaries:')
    for pkg in sorted(source.provides_binaries.keys()):
        print(f'  - {pkg}')

    print()
    print('* Build Dependencies:')
    for pkg, ver in sorted(source.build_dependencies.items()):
        print(f'  - {pkg}: {ver}')
