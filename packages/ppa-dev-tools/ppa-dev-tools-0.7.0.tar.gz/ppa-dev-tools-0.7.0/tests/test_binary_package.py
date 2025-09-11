#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2023 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests the BinaryPackage class as an interface to an Apt binary package record."""

import os
import sys

import pytest

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.binary_package import BinaryPackage


@pytest.mark.parametrize('pkg_dict, expected_repr, expected_str', [
    ({'package': 'a', 'architecture': 'b', 'version': '1'},
     "BinaryPackage(pkg_dict={'package': 'a', 'architecture': 'b', 'version': '1'})",
     'a (1) [b]'),
])
def test_object(pkg_dict, expected_repr, expected_str):
    """Checks that BinaryPackage objects can be instantiated."""
    obj = BinaryPackage(pkg_dict)

    assert obj
    assert repr(obj) == expected_repr
    assert str(obj) == expected_str


@pytest.mark.parametrize('pkg_dict, expected_exception', [
    ({}, ValueError),
    ({'package': 'x'}, ValueError),
    ({'architecture': 'x'}, ValueError),
    ({'version': 'x'}, ValueError),
    ({'package': None, 'architecture': None, 'version': None}, ValueError),
    ({'package': None, 'architecture': 'x',  'version': 'x'}, ValueError),
    ({'package': 'x',  'architecture': None, 'version': 'x'}, ValueError),
    ({'package': 'x',  'architecture': 'x',  'version': None}, ValueError),
])
def test_object_error(pkg_dict, expected_exception):
    """Checks that BinaryPackage objects can be instantiated."""
    with pytest.raises(expected_exception):
        obj = BinaryPackage(pkg_dict)
        assert obj


@pytest.mark.parametrize('pkg_dict, expected_binary_package_name', [
    ({'package': 'a',  'architecture': 'b',  'version': '1'}, 'a'),
])
def test_name(pkg_dict, expected_binary_package_name):
    """Checks the package name is obtained from pkg_dict."""
    binary_package = BinaryPackage(pkg_dict)

    assert binary_package.name == expected_binary_package_name


@pytest.mark.parametrize('pkg_info, expected_deps', [
    ({'package': 'x',  'architecture': 'x',  'version': 'x', 'depends': 'a'},
     {'a': ''}),
    ({'package': 'x',  'architecture': 'x',  'version': 'x', 'depends': 'a, b, c'},
     {'a': '', 'b': '', 'c': ''}),
    ({'package': 'x',  'architecture': 'x',  'version': 'x', 'depends': 'a | b | c'},
     {('a', 'b', 'c'): {'a': '', 'b': '', 'c': ''}}),
    ({'package': 'x',  'architecture': 'x',  'version': 'x', 'depends': 'a (= 1) | b (> 2) | c (<= 3)'},
     {('a', 'b', 'c'): {'a': '(= 1)', 'b': '(> 2)', 'c': '(<= 3)'}}),
    ({'package': 'x',  'architecture': 'x',  'version': 'x', 'depends': 'a (>= 1.0)'},
     {'a': '(>= 1.0)'}),
    ({'package': 'zlib1g-dev',  'architecture': 'amd64',  'version': '1:1.2.13.dfsg-1ubuntu4',
      'depends': 'zlib1g (= 1:1.2.13.dfsg-1ubuntu4), libc6-dev | libc-dev'},
     {('libc6-dev', 'libc-dev'): {'libc-dev': '', 'libc6-dev': ''},
      'zlib1g': '(= 1:1.2.13.dfsg-1ubuntu4)'}),
])
def test_installation_dependencies(pkg_info, expected_deps):
    """Checks that BinaryPackage objects parse their Dependencies field."""
    binary_package = BinaryPackage(pkg_info)

    assert binary_package.installation_dependencies == expected_deps


@pytest.mark.parametrize('pkg_info, expected_recommends', [
    ({'package': 'x',  'architecture': 'x',  'version': 'x', 'recommends': 'a'},
     {'a': ''}),
    ({'package': 'x',  'architecture': 'x',  'version': 'x', 'recommends': 'a'},
     {'a': ''}),
    ({'package': 'x',  'architecture': 'x',  'version': 'x', 'recommends': 'a, b, c'},
     {'a': '', 'b': '', 'c': ''}),
    ({'package': 'x',  'architecture': 'x',  'version': 'x', 'recommends': 'a | b | c'},
     {('a', 'b', 'c'): {'a': '', 'b': '', 'c': ''}}),
    ({'package': 'x',  'architecture': 'x',  'version': 'x', 'recommends': 'a (= 1) | b (> 2) | c (<= 3)'},
     {('a', 'b', 'c'): {'a': '(= 1)', 'b': '(> 2)', 'c': '(<= 3)'}}),
    ({'package': 'x',  'architecture': 'x',  'version': 'x', 'recommends': 'a (>= 1.0)'},
     {'a': '(>= 1.0)'}),
    ({'package': 'zlib1g-dev',  'architecture': 'amd64',  'version': '1:1.2.13.dfsg-1ubuntu4',
      'recommends': 'zlib1g (= 1:1.2.13.dfsg-1ubuntu4), libc6-dev | libc-dev'},
     {('libc6-dev', 'libc-dev'): {'libc-dev': '', 'libc6-dev': ''},
      'zlib1g': '(= 1:1.2.13.dfsg-1ubuntu4)'}),
])
def test_recommended_packages(pkg_info, expected_recommends):
    """Checks that BinaryPackage objects parse their Recommends field."""
    binary_package = BinaryPackage(pkg_info)

    assert binary_package.recommended_packages == expected_recommends
