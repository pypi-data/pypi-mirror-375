#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2024 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests SourcePublication class as representing a package release."""

import os
import sys

import pytest

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.source_publication import SourcePublication  # noqa: E402


@pytest.mark.parametrize('pub_dict', [
    ({'package': 'pkg', 'version': 'ver', 'series': 'ser'}),
    ({'package': 'pkg2.0-abc', 'version': '1.0-1', 'series': 'noble'}),
    ({'package': 'dovecot', 'version': '1.2.3', 'series': 'noble', 'archive': 'ppa:me/myppa'}),
])
def test_object(pub_dict):
    """Check that SourcePublication objects can be instantiated."""
    assert SourcePublication(**pub_dict)


@pytest.mark.parametrize('pub_dict, expected_exception', [
    ({}, TypeError),
    ({'package': 'x'}, TypeError),
    ({'version': 'x'}, TypeError),
    ({'series': 'x'}, TypeError),
    ({'package': None, 'version': None, 'series': None}, ValueError),
    ({'package': None, 'version': 'x',  'series': None}, ValueError),
    ({'package': 'x',  'version': None, 'series': None}, ValueError),
    ({'package': 'x',  'version': 'x',  'series': None}, ValueError),
    ({'package': 'x',  'version': 'x',  'series': None}, ValueError),
    ({'package': None, 'version': 'x',  'series': 'x'}, ValueError),
])
def test_object_error(pub_dict, expected_exception):
    """Check that SourcePublication objects can be instantiated."""
    with pytest.raises(expected_exception):
        source_publication = SourcePublication(**pub_dict)
        assert source_publication


@pytest.mark.parametrize('pub_dict, expected_repr', [
    (
        {'package': 'pkg', 'version': 'ver', 'series': 'ser'},
        "SourcePublication(package='pkg', version='ver', series='ser', archive=None, status=None)",
    ),
    (
        {'package': 'pkg', 'version': '1.2.3', 'series': 'noble', 'archive': 'ppa:me/myppa', 'status': 'pass'},
        "SourcePublication(package='pkg', version='1.2.3', series='noble', archive='ppa:me/myppa', status='pass')",
    ),
])
def test_repr(pub_dict, expected_repr):
    """Check that SourcePublication objects can be instantiated."""
    source_publication = SourcePublication(**pub_dict)
    assert repr(source_publication) == expected_repr


@pytest.mark.parametrize('pub_dict, expected_str', [
    (
        {'package': 'pkg', 'version': 'ver', 'series': 'ser'},
        "ser/pkg/ver",
    ),
    (
        {'package': 'pkg', 'version': '1.2.3', 'series': 'noble', 'archive': 'ppa:me/myppa'},
        "noble/pkg/1.2.3 (ppa:me/myppa)",
    ),
])
def test_str(pub_dict, expected_str):
    """Check that SourcePublication objects can be instantiated."""
    source_publication = SourcePublication(**pub_dict)
    assert str(source_publication) == expected_str


@pytest.mark.parametrize('pub_dict, expected_dict', [
    (
        {'package': 'pkg', 'version': 'ver', 'series': 'ser'},
        {'package': 'pkg', 'version': 'ver', 'series': 'ser', 'archive': None, 'status': None},
    ),
    (
        {'package': 'pkg', 'version': '1.2.3', 'series': 'noble', 'archive': 'ppa:me/myppa', 'status': 'pass'},
        {'package': 'pkg', 'version': '1.2.3', 'series': 'noble', 'archive': 'ppa:me/myppa', 'status': 'pass'},
    ),
])
def test_to_dict(pub_dict, expected_dict):
    """Check that SourcePublication objects can be instantiated."""
    source_publication = SourcePublication(**pub_dict)
    assert source_publication.to_dict() == expected_dict


@pytest.mark.parametrize('pub_dict, expected_url', [
    (
        {'package': 'pkg', 'version': 'x', 'series': 'ser'},
        'https://autopkgtest.ubuntu.com/packages/p/pkg/ser'
    ),
    (
        {'package': 'libabc', 'version': 'x', 'series': 'noble'},
        'https://autopkgtest.ubuntu.com/packages/liba/libabc/noble'
    ),
])
def test_autopkgtest_history_url(pub_dict, expected_url):
    """Check that valid history URLs are generated."""
    source_publication = SourcePublication(**pub_dict)
    assert source_publication.autopkgtest_history_url == expected_url
