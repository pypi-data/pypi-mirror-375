#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2023 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

# pylint: disable=protected-access,line-too-long

"""Tests the Suite class as an interface to Apt suite records."""

import os
import sys

import lzma as xz
import pytest

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

from ppa.suite import Suite
from ppa.source_package import SourcePackage
from ppa.binary_package import BinaryPackage


@pytest.mark.parametrize('suite_name, cache_dir, expected_repr, expected_str', [
    ('x', '/tmp', "Suite(suite_name='x', cache_dir='/tmp')", "x"),
    ('a-1', '/tmp', "Suite(suite_name='a-1', cache_dir='/tmp')", "a-1"),
    ('b-2', '/tmp', "Suite(suite_name='b-2', cache_dir='/tmp')", "b-2"),
])
def test_object(suite_name, cache_dir, expected_repr, expected_str):
    """Checks that Suite objects can be instantiated."""
    suite = Suite(suite_name, cache_dir)

    assert suite
    assert repr(suite) == expected_repr
    assert str(suite) == expected_str


@pytest.mark.parametrize('suite_name, cache_dir, expected_exception', [
    ('x', '', ValueError),
    ('', 'x', ValueError),
    ('x', 'x', FileNotFoundError),
    ('', '', ValueError),
    ('a-1', None, ValueError),
    (None, 'x', ValueError),
    (None, None, ValueError),
])
def test_object_error(suite_name, cache_dir, expected_exception):
    """Checks that Suite objects handle invalid input properly."""
    with pytest.raises(expected_exception):
        suite = Suite(suite_name, cache_dir)
        assert suite


@pytest.mark.parametrize('release_contents, expected_info', [
    ('a: 1', {'a': '1'}),
    ("""
Origin: Ubuntu
Label: Ubuntu
Suite: lunar
Version: 23.04
Codename: lunar
Date: Tue, 28 Feb 2023 19:49:32 UTC
Architectures: amd64 arm64 armhf i386 ppc64el riscv64 s390x
Components: main restricted universe multiverse
Description: Ubuntu Lunar 23.04
    """, {
        'Suite': 'lunar',
        'Codename': 'lunar',
        'Architectures': 'amd64 arm64 armhf i386 ppc64el riscv64 s390x',
        'Components': 'main restricted universe multiverse',
    }), ("""
Origin: Ubuntu
Label: Ubuntu
Suite: lunar-proposed
Version: 23.04
Codename: lunar
Date: Tue, 28 Feb 2023 19:50:27 UTC
Architectures: amd64 arm64 armhf i386 ppc64el riscv64 s390x
Components: main restricted universe multiverse
Description: Ubuntu Lunar Proposed
NotAutomatic: yes
ButAutomaticUpgrades: yes
MD5Sum:
 7de6b7c0ed6b4bfb662e07fbc449dfdd        148112816 Contents-amd64
    """, {
        'Suite': 'lunar-proposed',
        'Codename': 'lunar',
        'NotAutomatic': 'yes'
    }),
])
def test_info(tmp_path, release_contents, expected_info):
    """Checks the parsing of info loaded from the Release file."""
    # Create Release file using release_contents in synthetic tree
    suite_dir = tmp_path / 'x'
    suite_dir.mkdir()
    release_file = suite_dir / 'Release'
    release_file.write_text(release_contents)

    suite = Suite(suite_dir.name, suite_dir)

    # Verify the expected items are present in the suite's info dict
    for key, value in expected_info.items():
        assert key in suite.info.keys()
        assert suite.info[key] == value


@pytest.mark.parametrize('info, expected_series_codename', [
    ({'Suite': 'x'}, 'x'),
    ({'Suite': 'x-y'}, 'x'),
    ({'Suite': 'lunar'}, 'lunar'),
    ({'Suite': 'lunar-proposed'}, 'lunar'),
    ({'Suite': 'focal-security'}, 'focal'),
])
def test_series_codename(monkeypatch, info, expected_series_codename):
    """Checks the codename is extracted properly from the suite name."""
    suite = Suite('x', '/tmp')

    # Substitute in our fake test info in place of Suite's info() routine
    monkeypatch.setattr(Suite, "info", info)

    assert suite.series_codename == expected_series_codename


@pytest.mark.parametrize('info, expected_pocket', [
    ({'Suite': 'x'}, 'release'),
    ({'Suite': 'x-backports'}, 'backports'),
    ({'Suite': 'lunar'}, 'release'),
    ({'Suite': 'lunar-proposed'}, 'proposed'),
    ({'Suite': 'focal-security'}, 'security'),
])
def test_pocket(monkeypatch, info, expected_pocket):
    """Checks the pocket is extracted properly from the suite name."""
    suite = Suite('x', '/tmp')

    # Substitute in our fake test info in place of Suite's info() routine
    monkeypatch.setattr(Suite, "info", info)

    assert suite.pocket == expected_pocket


@pytest.mark.parametrize('info, expected_architectures', [
    ({'Architectures': 'x y z'}, ['x', 'y', 'z']),
    ({'Architectures': 'x y z'}, ['x', 'y', 'z']),
    ({'Architectures': 'amd64 arm64 armhf i386 ppc64el riscv64 s390x'},
     ['amd64', 'arm64', 'armhf', 'i386', 'ppc64el', 'riscv64', 's390x']),
])
def test_architectures(monkeypatch, info, expected_architectures):
    """Checks that the architecture list is parsed from the info dict."""
    suite = Suite('x', '/tmp')

    # Substitute in our fake test info in place of Suite's info() routine
    monkeypatch.setattr(Suite, "info", info)

    assert sorted(suite.architectures) == sorted(expected_architectures)


@pytest.mark.parametrize('suite_name, component_paths, expected_components', [
    ('a-1', ['a-1/main', 'a-1/universe', 'a-1/multiverse'], ['main', 'universe', 'multiverse']),
    ('a-1', ['a-1/main', 'b-1/universe', 'c-1/multiverse'], ['main']),
    ('a-1', ['a-1/main', 'a-1/main/y', 'c-1/multiverse/x'], ['main']),
    ('x', ['x/main', 'x/restricted', 'x/universe', 'x/multiverse'],
     ['main', 'restricted', 'universe', 'multiverse']),
])
def test_components(tmp_path, suite_name, component_paths, expected_components):
    """Checks that the components are read from the Apt directory tree.

    The repository could have multiple suites (b-1, c-1, ...)
    so we specify that we're just looking for the components in
    @param suite_name.
    """
    # Stub in suite's directory structure with component subdirs
    for component_path in component_paths:
        component_dir = tmp_path / component_path
        component_dir.mkdir(parents=True)

    suite = Suite(suite_name, tmp_path / suite_name)

    assert sorted(suite.components) == sorted(expected_components)


@pytest.mark.parametrize('sources_contents, expected_sources', [
    ('Package: a\nVersion: b\nBinary: c',
     {'a': SourcePackage({'Package': 'a', 'Version': 'b', 'Binary': 'c'})}),
    ("""
Package: aalib
Version:
Binary:

Package: abseil
Version:
Binary:

Package: accountsservice
Version:
Binary:

Package: acct
Version:
Binary:
    """, {
        'aalib': SourcePackage({'Package': 'aalib', 'Version': '', 'Binary': ''}),
        'abseil': SourcePackage({'Package': 'abseil', 'Version': '', 'Binary': ''}),
        'accountsservice': SourcePackage({'Package': 'accountsservice', 'Version': '', 'Binary': ''}),
        'acct': SourcePackage({'Package': 'acct', 'Version': '', 'Binary': ''}),
    }),
    ("""
Package: libsigc++-2.0
Format: 3.0 (quilt)
Binary: libsigc++-2.0-0v5, libsigc++-2.0-dev, libsigc++-2.0-doc
Architecture: any all
Version: 2.12.0-1
Priority: optional
Section: devel
Maintainer: Debian GNOME Maintainers <pkg-gnome-maintainers@lists.alioth.debian.org>
Uploaders: Jeremy Bicha <jbicha@ubuntu.com>, Michael Biebl <biebl@debian.org>
Standards-Version: 4.6.1
Build-Depends: debhelper-compat (= 13), dh-sequence-gnome, docbook-xml, docbook-xsl, doxygen, graphviz, libxml2-utils <!nocheck>, meson (>= 0.50.0), mm-common (>= 1.0.0), python3-distutils, xsltproc
Homepage: https://libsigcplusplus.github.io/libsigcplusplus/
Vcs-Browser: https://salsa.debian.org/gnome-team/libsigcplusplus
Vcs-Git: https://salsa.debian.org/gnome-team/libsigcplusplus.git
Directory: pool/main/libs/libsigc++-2.0
Package-List:
 libsigc++-2.0-0v5 deb libs optional arch=any
 libsigc++-2.0-dev deb libdevel optional arch=any
 libsigc++-2.0-doc deb doc optional arch=all
Files:
 23feb2cc5036384f94a3882c760a7eb4 2336 libsigc++-2.0_2.12.0-1.dsc
 8685af8355138b1c48a6cd032e395303 163724 libsigc++-2.0_2.12.0.orig.tar.xz
 d60ca8c15750319f52d3b7eaeb6d99e1 10800 libsigc++-2.0_2.12.0-1.debian.tar.xz
Checksums-Sha1:
 81840b1d39dc48350de207566c86b9f1ea1e22d2 2336 libsigc++-2.0_2.12.0-1.dsc
 f66e696482c4ff87968823ed17b294c159712824 163724 libsigc++-2.0_2.12.0.orig.tar.xz
 a699c88f7c91157af4c5cdd0f4d0ddebeea9092e 10800 libsigc++-2.0_2.12.0-1.debian.tar.xz
    """,  # noqa: E501
        {
            'libsigc++-2.0': SourcePackage({
                'Package': 'libsigc++-2.0',
                'Version': '2.12.0-1',
                'Binary': 'libsigc++-2.0-0v5, libsigc++-2.0-dev, libsigc++-2.0-doc',
            }),
        }),
])
def test_sources(tmp_path, sources_contents, expected_sources):
    """Checks that the source packages are read from the Apt record.

    We don't care about the SourcePackage object itself (the value in
    @param expected_sources is just a placeholder), but need to ensure
    the Sources.xz file is read and the expected list of packages
    parsed out of it.
    """
    # Create Sources.xz file using sources_contents in synthetic tree
    suite_dir = tmp_path / 'x'
    suite_dir.mkdir()
    component_dir = suite_dir / 'main'
    component_dir.mkdir()
    arch_dir = component_dir / 'source'
    arch_dir.mkdir()
    sources_file = arch_dir / 'Sources.xz'
    sources_file.write_bytes(xz.compress(str.encode(sources_contents)))

    # Create the suite to wrapper our path and access Sources.xz
    suite = Suite(suite_dir.name, suite_dir)

    assert sorted(suite.sources) == sorted(expected_sources)


@pytest.mark.parametrize('architectures, packages_contents, expected_binaries', [
    (['x'], 'Package: a\nVersion:\nArchitecture: x',
     {'a:x': BinaryPackage({'Package': 'a', 'Version': '', 'Architecture': ''})}),
    (['amd64'], """
Package: aalib
Version:
Architecture:

Package: abseil
Version:
Architecture:

Package: accountsservice
Version:
Architecture:

Package: acct
Version:
Architecture:
    """,
     {
        'aalib:amd64': BinaryPackage({'Package': 'aalib', 'Version': '', 'Architecture': ''}),
        'abseil:amd64': BinaryPackage({'Package': 'abseil', 'Version': '', 'Architecture': ''}),
        'accountsservice:amd64': BinaryPackage({'Package': 'accountsservice', 'Version': '', 'Architecture': ''}),
        'acct:amd64': BinaryPackage({'Package': 'acct', 'Version': '', 'Architecture': ''}),
     }),
    (['amd64'], """
Package: accountsservice
Architecture: amd64
Version: 22.08.8-1ubuntu4
Priority: optional
Section: gnome
Origin: Ubuntu
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
Original-Maintainer: Debian freedesktop.org maintainers <pkg-freedesktop-maintainers@lists.alioth.debian.org>
Bugs: https://bugs.launchpad.net/ubuntu/+filebug
Installed-Size: 504
Depends: dbus (>= 1.9.18), libaccountsservice0 (= 22.08.8-1ubuntu4), libc6 (>= 2.34), libglib2.0-0 (>= 2.63.5), libpolkit-gobject-1-0 (>= 0.99)
Recommends: default-logind | logind
Suggests: gnome-control-center
Filename: pool/main/a/accountsservice/accountsservice_22.08.8-1ubuntu4_amd64.deb
Size: 68364
MD5sum: a10447714f0ce3c5f607b7b27c0f9299
SHA1: 252482d8935d16b7fc5ced0c88819eeb7cad6c65
SHA256: 4e341a8e288d8f8f9ace6cf90a1dcc3211f06751d9bec3a68a6c539b0c711282
SHA512: eb91e21b4dfe38e9768e8ca50f30f94298d86f07e78525ab17df12eb3071ea21cfbdc2ade3e48bd4e22790aa6ce3406bb10fbd17d8d668f84de1c8adeee249cb
Homepage: https://www.freedesktop.org/wiki/Software/AccountsService/
Description: query and manipulate user account information
Task: ubuntu-desktop-minimal, ubuntu-desktop, ubuntu-desktop-raspi, ubuntu-wsl, kubuntu-desktop, xubuntu-minimal, xubuntu-desktop, lubuntu-desktop, ubuntustudio-desktop-core, ubuntustudio-desktop, ubuntukylin-desktop, ubuntu-mate-core, ubuntu-mate-desktop, ubuntu-budgie-desktop, ubuntu-budgie-desktop-raspi, ubuntu-unity-desktop, edubuntu-desktop-minimal, edubuntu-desktop, edubuntu-desktop-raspi, edubuntu-wsl
Description-md5: 8aeed0a03c7cd494f0c4b8d977483d7e
    """,
     {  # noqa: E501
       'accountsservice:amd64': BinaryPackage({
           'Package': 'accountsservice',
           'Version': '',
           'Architecture': 'amd64'
        })
     }),
    (
        ['amd64', 'arm64', 'armhf', 'i386', 'ppc64el', 'riscv64', 's390x'],
        'Package: libsigc++-2.0\nVersion:\nArchitecture: amd64 arm64 armhf i386 ppc64el riscv64 s390x\n',
        {
            'libsigc++-2.0:amd64': BinaryPackage({
                'Package': 'libsigc++-2.0', 'Version': '', 'Architecture': 'amd64'}),
            'libsigc++-2.0:arm64': BinaryPackage({
                'Package': 'libsigc++-2.0', 'Version': '', 'Architecture': 'arm64'}),
            'libsigc++-2.0:armhf': BinaryPackage({
                'Package': 'libsigc++-2.0', 'Version': '', 'Architecture': 'armhf'}),
            'libsigc++-2.0:i386': BinaryPackage({
                'Package': 'libsigc++-2.0', 'Version': '', 'Architecture': 'i386'}),
            'libsigc++-2.0:ppc64el': BinaryPackage({
                'Package': 'libsigc++-2.0', 'Version': '', 'Architecture': 'ppc64el'}),
            'libsigc++-2.0:riscv64': BinaryPackage({
                'Package': 'libsigc++-2.0', 'Version': '', 'Architecture': 'riscv64'}),
            'libsigc++-2.0:s390x': BinaryPackage({
                'Package': 'libsigc++-2.0', 'Version': '', 'Architecture': 's390x'}),
        },
    ),
])
def test_binaries(tmp_path, architectures, packages_contents, expected_binaries):
    """Checks that the binary packages are read from the Apt record.

    We don't care about the BinaryPackage (the value) itself, just that
    the package name and arch are registered correctly, and that typical
    Packages.xz files are processed as intended.
    """
    suite_dir = tmp_path / 'x'
    suite_dir.mkdir()
    release_file = suite_dir / 'Release'
    release_file.write_text(f'Architectures: {" ".join(architectures)}')
    component_dir = suite_dir / 'main'
    component_dir.mkdir()
    for arch in architectures:
        arch_dir = component_dir / f'binary-{arch}'
        arch_dir.mkdir()
        packages_file = arch_dir / 'Packages.xz'
        packages_file.write_bytes(xz.compress(str.encode(packages_contents)))

    # Create the suite to wrapper our path and access Packages.xz
    suite = Suite(suite_dir.name, suite_dir)
    assert sorted(suite.binaries.keys()) == sorted(expected_binaries.keys())


@pytest.mark.parametrize('sources, expected_rdepends, expected_provides', [
    ({}, [], []),
    (
        {'a': SourcePackage({'Package': 'a', 'Version': 'x', 'Build-Depends': 'a', 'Binary': 'x'})},
        ['a'],
        ['x']
    ),
    (
        {'a': SourcePackage({'Package': 'a', 'Version': 'x', 'Build-Depends': 'a, b, c', 'Binary': 'x'})},
        ['a', 'b', 'c'],
        ['x']
    ),
    (
        {
            'a': SourcePackage({'Package': 'a', 'Version': 'x', 'Binary': 'a1'}),
            'b': SourcePackage({'Package': 'b', 'Version': 'x', 'Build-Depends': 'a1', 'Binary': 'b1'}),
            'c': SourcePackage({'Package': 'c', 'Version': 'x', 'Build-Depends': 'a1, b1', 'Binary': 'c1'}),
        },
        ['a1', 'b1'],
        ['a1', 'b1', 'c1']
    ),
    (
        {'a': SourcePackage({'Package': 'a', 'Version': 'x', 'Binary': 'a'})},
        [],
        ['a']),
    (
        {'a': SourcePackage({'Package': 'a', 'Version': 'x', 'Binary': 'a, b, c'})},
        [],
        ['a', 'b', 'c']
    ),
    (
        {
            'dovecot': SourcePackage(
                {
                    'Package': 'dovecot',
                    'Version': '1:2.3.19.1+dfsg1-2ubuntu4',
                    'Binary': 'dovecot-core, dovecot-dev, dovecot-imapd, dovecot-pop3d, dovecot-lmtpd, dovecot-managesieved, dovecot-pgsql, dovecot-mysql, dovecot-sqlite, dovecot-ldap, dovecot-gssapi, dovecot-sieve, dovecot-solr, dovecot-lucene, dovecot-submissiond, dovecot-auth-lua',  # noqa: E501
                    'Architecture': 'any',
                    'Build-Depends': 'debhelper-compat (= 13), default-libmysqlclient-dev, krb5-multidev, libapparmor-dev [linux-any], libbz2-dev, libcap-dev [linux-any], libclucene-dev, libdb-dev, libexpat-dev, libexttextcat-dev, libicu-dev, libldap2-dev, liblua5.3-dev, liblz4-dev, liblzma-dev, libpam0g-dev, libpq-dev, libsasl2-dev, libsodium-dev, libsqlite3-dev, libssl-dev, libstemmer-dev, libsystemd-dev [linux-any], libunwind-dev [amd64 arm64 armel armhf hppa i386 ia64 mips mips64 mips64el mipsel powerpc powerpcspe ppc64 ppc64el sh4], libwrap0-dev, libzstd-dev, lsb-release, pkg-config, zlib1g-dev',  # noqa: E501
                    'Testsuite-Triggers': 'lsb-release, python3, systemd-sysv',
                }
            )
        },
        [
            'debhelper-compat',
            'default-libmysqlclient-dev',
            'krb5-multidev',
            'libapparmor-dev',
            'libbz2-dev',
            'libcap-dev',
            'libclucene-dev',
            'libdb-dev',
            'libexpat-dev',
            'libexttextcat-dev',
            'libicu-dev',
            'libldap2-dev',
            'liblua5.3-dev',
            'liblz4-dev',
            'liblzma-dev',
            'libpam0g-dev',
            'libpq-dev',
            'libsasl2-dev',
            'libsodium-dev',
            'libsqlite3-dev',
            'libssl-dev',
            'libstemmer-dev',
            'libsystemd-dev',
            'libunwind-dev',
            'libwrap0-dev',
            'libzstd-dev',
            'lsb-release',
            'pkg-config',
            'zlib1g-dev',
        ],
        [
            'dovecot-core',
            'dovecot-dev',
            'dovecot-imapd',
            'dovecot-pop3d',
            'dovecot-lmtpd',
            'dovecot-managesieved',
            'dovecot-pgsql',
            'dovecot-mysql',
            'dovecot-sqlite',
            'dovecot-ldap',
            'dovecot-gssapi',
            'dovecot-sieve',
            'dovecot-solr',
            'dovecot-lucene',
            'dovecot-submissiond',
            'dovecot-auth-lua',
        ]
    ),
])
def test_rebuild_tables(monkeypatch, sources, expected_rdepends, expected_provides):
    """Checks generation of the internal lookup tables for provides and rdepends."""
    monkeypatch.setattr(Suite, "sources", sources)
    # Verify provides and rdepends table are as expected
    suite = Suite('x', '/tmp')
    suite._rebuild_lookup_tables()

    assert sorted(suite._rdepends_table.keys()) == sorted(expected_rdepends)
    assert sorted(suite._provides_table.keys()) == sorted(expected_provides)


def test_rebuild_tables_mapping(monkeypatch):
    """Checks the mapping of rdepends to provides in the generated tables.

    The two lookup tables are essential to the rdepends test functionality
    since they define the mappings between various source package provides
    and depends.  This test builds a synthetic collection of source packages,
    generates the tables, and then verifies the tables can be used to lookup
    the appropriate related packages.

    For purposes of this test, we assume each source package provides
    binaries of the same name appended with either '1' or '2'.

    Also, note that the packages are set up with a circular dependency
    (a depends on c, but c depends on a).  This is an unhealthy
    situation for an archive to be in, but it certainly does happen in
    the wild.  We're just setting it up that way for convenience since
    we can then assume all provided binaries will be required by
    something in the archive.
    """
    sources = {
        'a': SourcePackage({'Package': 'a', 'Version': 'x', 'Build-Depends': 'c1', 'Binary': 'a1'}),
        'b': SourcePackage({'Package': 'b', 'Version': 'x', 'Build-Depends': 'a1, c2', 'Binary': 'b1'}),
        'c': SourcePackage({'Package': 'c', 'Version': 'x', 'Build-Depends': 'a1, b1', 'Binary': 'c1, c2'}),
    }
    monkeypatch.setattr(Suite, "sources", sources)
    suite = Suite('x', '/tmp')
    suite._rebuild_lookup_tables()

    # Check the integrity of the lookup tables for the sources we gave it
    for source in sources.values():
        # Verify our dependency is satisfied by a SourcePackage in the collection
        for dependency in source.build_dependencies:
            assert dependency in suite._provides_table
            package = suite._provides_table[dependency]
            assert isinstance(package, SourcePackage)
            assert dependency in [f"{package.name}1", f"{package.name}2"]

        # Verify SourcePackages that depend on us can be located
        for binary in source.provides_binaries:
            assert binary in suite._rdepends_table
            for package in suite._rdepends_table[binary]:
                assert isinstance(package, SourcePackage)
                assert binary in package.build_dependencies


@pytest.mark.parametrize('sources_dict, source_package_name, expected_packages', [
    pytest.param(
        [{'Package': 'a', 'Version': 'x', 'Binary': 'a1'}], 'a', [],
        marks=pytest.mark.xfail(reason='Does not handle undefined build-depends'),
    ),
    pytest.param(
        [{'Package': 'a', 'Version': 'x', 'Build-Depends': None, 'Binary': 'a1'}], 'a', [],
        marks=pytest.mark.xfail(reason='Does not handle undefined build-depends'),
    ),
    pytest.param(
        [{'Package': 'a', 'Version': 'x', 'Build-Depends': '', 'Binary': 'a1'}], 'a', [],
        marks=pytest.mark.xfail(reason='Does not handle undefined build-depends'),
    ),

    (
        [
            {'Package': 'a', 'Version': 'x', 'Build-Depends': 'b1', 'Binary': 'a1'},
            {'Package': 'b', 'Version': 'x', 'Build-Depends': 'a1', 'Binary': 'b1'},
            {'Package': 'c', 'Version': 'x', 'Build-Depends': 'b1', 'Binary': 'c1'},
        ],
        'a',
        ['b'],
    ),

    (
        [
            {'Package': 'a', 'Version': 'x', 'Build-Depends': 'd1', 'Binary': 'a1'},
            {'Package': 'b', 'Version': 'x', 'Build-Depends': 'a1', 'Binary': 'b1'},
            {'Package': 'c', 'Version': 'x', 'Build-Depends': 'b1', 'Binary': 'c1, c2'},
            {'Package': 'd', 'Version': 'x', 'Build-Depends': 'a1, b1, c2', 'Binary': 'd1'},
        ],
        'd',
        ['a'],
    ),
])
def test_dependent_packages(monkeypatch, sources_dict, source_package_name, expected_packages):
    '''Checks that dependent_packages() returns the right packages to test.

    This member function is the main API for looking up what packages
    should have autopkgtests run, triggered against our desired package.
    '''
    sources = {pkg['Package']: SourcePackage(pkg) for pkg in sources_dict}

    monkeypatch.setattr(
        Suite,
        "sources",
        sources
    )
    suite = Suite('x', '/tmp')
    source_package = sources[source_package_name]

    assert sorted(suite.dependent_packages(source_package)) == expected_packages
