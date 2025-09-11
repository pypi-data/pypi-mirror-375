#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2022 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests the Subtest class as representing components of an autopkgtest run."""

import os
import sys
import json

import pytest

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.subtest import Subtest


def test_object():
    """Checks that Subtest objects can be instantiated."""
    subtest = Subtest('a UNKNOWN')
    # TODO: If no ':' in description, should throw exception?
    # TODO: Or add a function that parses lines and returns subtests?
    assert subtest


def test_repr():
    """Checks Subtest object representation."""
    subtest = Subtest('a PASS')
    assert repr(subtest) == "Subtest(line='a PASS')"


def test_str():
    """Checks Subtest object textual presentation."""
    subtest = Subtest('a PASS')
    assert 'PASS' in f"{subtest}"
    assert 'a' in f"{subtest}"
    assert '🟩' in f"{subtest}"


def test_to_dict():
    """Checks Subtest object structural representation."""
    subtest = Subtest('a PASS')
    expected_keys = ['desc', 'line', 'status', 'status_icon']
    expected_types = [str]

    d = subtest.to_dict()
    assert isinstance(d, dict), f"type of d is {type(d)} not dict"

    # Verify expected keys are present
    assert sorted(d.keys()) == sorted(expected_keys)

    # Verify values are within set of expected types
    for k, v in d.items():
        assert type(v) in expected_types, f"'{k}={v}' is unexpected type {type(v)}"

    # Verify full dict can be written as JSON
    try:
        assert json.dumps(d)
    except UnicodeDecodeError as e:
        assert False, f"Wrong UTF codec detected: {e}"
    except json.JSONDecodeError as e:
        assert False, f"JSON decoding error: {e.msg}, {e.doc}, {e.pos}"


def test_desc():
    """Checks Subtest description is parsed correctly."""
    subtest = Subtest('a PASS')
    assert subtest.desc == 'a'

    subtest = Subtest('a FAIL descriptive text')
    assert subtest.desc == 'a'

    subtest = Subtest('a:b  PASS')
    assert subtest.desc == 'a:b'


@pytest.mark.parametrize('line, status', [
    ('a PASS', 'PASS'),
    ('b SKIP', 'SKIP'),
    ('c FAIL', 'FAIL'),
    ('d FAIL non-zero exit status 123', 'FAIL'),
    ('librust-clang-sys-dev:clang_10_0 FAIL non-zero exit status 101', 'FAIL'),
    ('librust-clang-sys-dev:static FLAKY non-zero exit status 101', 'FLAKY'),
    ('f BAD', 'BAD'),
    ('g UNKNOWN', 'UNKNOWN'),
    ('h invalid', 'UNKNOWN'),
    ('i bAd', 'UNKNOWN'),
])
def test_status(line, status):
    """Checks Subtest status is parsed correctly."""
    subtest = Subtest(line)
    assert subtest.status == status

    subtest = Subtest('a PASS')


@pytest.mark.parametrize('line, icon', [
    ('x PASS', "🟩"),
    ('x SKIP', "🟧"),
    ('x FAIL', "🟥"),
    ('x FLAKY', "🟫"),
    ('x BAD', "⛔"),
    ('x UNKNOWN', "⚪"),
    ('x invalid', "⚪"),
    ('x bAd', "⚪"),
])
def test_status_icon(line, icon):
    """Checks Subtest provides correct icon for status.

    :param str line: Subtest status line to be parsed.
    :param str icon: Resulting status icon that should be returned.
    """
    subtest = Subtest(line)
    assert subtest.status_icon == icon
