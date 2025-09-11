#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2023 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests SourcePackage as an interface to an Apt source package record."""

import os
import sys

import pytest

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.source_package import SourcePackage


@pytest.mark.parametrize('pkg_dict, expected_repr, expected_str', [
    ({'package': 'a', 'version': 'b', 'binary': 'c'},
     "SourcePackage(pkg_dict={'package': 'a', 'version': 'b', 'binary': 'c'})",
     "a (b)",
     ),
])
def test_object(pkg_dict, expected_repr, expected_str):
    """Checks that SourcePackage objects can be instantiated."""
    source_package = SourcePackage(pkg_dict)

    assert source_package
    assert repr(source_package) == expected_repr
    assert str(source_package) == expected_str


@pytest.mark.parametrize('pkg_dict, expected_exception', [
    ({}, ValueError),
    ({'package': 'x'}, ValueError),
    ({'version': 'x'}, ValueError),
    ({'binary': 'x'}, ValueError),
    ({'package': None, 'version': None, 'binary': None}, ValueError),
    ({'package': None, 'version': 'x',  'binary': 'x'}, ValueError),
    ({'package': 'x',  'version': None, 'binary': 'x'}, ValueError),
    ({'package': 'x',  'version': 'x',  'binary': None}, ValueError),
])
def test_object_error(pkg_dict, expected_exception):
    """Checks that SourcePackage objects can be instantiated."""
    with pytest.raises(expected_exception):
        source_package = SourcePackage(pkg_dict)
        assert source_package


@pytest.mark.parametrize('pkg_dict, expected_binaries', [
    ({'package': 'x', 'version': 'x', 'binary': 'a, b, c'},
     {'a': '', 'b': '', 'c': ''}),
    ({'package': 'dovecot',
      'version': '1:2.3.19.1+dfsg1-2ubuntu4',
      'binary': 'dovecot-core, dovecot-dev, dovecot-imapd, dovecot-pop3d, dovecot-lmtpd'},
     {'dovecot-core': '',
      'dovecot-dev': '',
      'dovecot-imapd': '',
      'dovecot-pop3d': '',
      'dovecot-lmtpd': '',
      }),
])
def test_provides_binaries(pkg_dict, expected_binaries):
    """Checks that SourcePackage objects parse their Provides field."""
    source_package = SourcePackage(pkg_dict)

    assert source_package.provides_binaries == expected_binaries


@pytest.mark.parametrize('pkg_dict, expected_build_dependencies', [
    ({'package': 'x', 'version': 'x', 'binary': '', 'build-depends': 'a, b, c [x]'},
     {'a': '', 'b': '', 'c': '[x]'}),
])
def test_build_dependencies(pkg_dict, expected_build_dependencies):
    """Checks that SourcePackage objects parse BuildDepends field."""
    source_package = SourcePackage(pkg_dict)

    assert source_package.build_dependencies == expected_build_dependencies
