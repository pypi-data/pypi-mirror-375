#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2019 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests the Ppa class as an interface to Launchpad's Ppa API."""

import os
import sys
import time
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.constants import URL_AUTOPKGTEST
from ppa.ppa import Ppa, ppa_address_split, get_ppa
from ppa.ppa_group import PpaGroup
from ppa.result import Result

from helpers import LpServiceMock


def test_object():
    """Check that PPA objects can be instantiated."""
    ppa = Ppa('test-ppa-name', 'test-owner-name', ppa_description='test-desc', service='test-svc')
    assert ppa
    assert ppa.ppa_name == 'test-ppa-name'
    assert ppa.owner_name == 'test-owner-name'
    assert ppa.ppa_description == 'test-desc'


def test_repr():
    """Check Ppa object representation."""
    ppa = Ppa('a', 'b', 'c', 'd')
    assert repr(ppa) == "Ppa(ppa_name='a', owner_name='b')"


def test_str():
    """Check Ppa object textual presentation."""
    ppa = Ppa('a', 'b', 'c', 'd')
    assert f"{ppa}" == 'b/a'


def test_address():
    """Check getting the PPA address."""
    ppa = Ppa('test', 'owner')
    assert ppa.address == "ppa:owner/test"


def test_description():
    """Check specifying a description when creating a PPA."""
    ppa = Ppa('test-ppa-name', 'test-owner-name', 'test-description')

    assert 'test-description' in ppa.ppa_description


@pytest.mark.parametrize('releases, architectures, expected_num_results, expected_num_triggers', [
    ([], [], 0, 0),
    (['x'], ['amd64'], 1, 1),
    (['x', 'y', 'z'], ['amd64'], 3, 1),
    (['x'], ['amd64', 'armhf', 'i386'], 1, 3),
    (['x', 'y', 'z'], ['amd64', 'armhf', 'i386'], 3, 3),
])
@patch('ppa.ppa.get_results')
@patch('ppa.ppa.open_url')
def test_get_autopkgtest_results(mock_open_url, mock_get_results,
                                 releases, architectures, expected_num_results, expected_num_triggers):
    """Check that autopkgtest results are retrieved and iterated correctly."""
    owner_name = 'a'
    ppa_name = 'b'

    # Bypass open_url() entirely so we don't try to retrieve anything.
    # Usually this returns a response that if valid is then passed to
    # get_results(), but since we'll be patching get_results(), all that
    # matters is that validity check passes.  We can do that by having
    # our mock open_url return a generic valid value, True.
    mock_open_url.return_value = True

    # Substitute in our fake results to be returned by get_results().
    # We need to have semi-valid looking URLs to pass internal checks,
    # but can provide trivially fake data.
    fake_results = {}
    fake_data_url = "https://fake.data"
    timestamp = time.strptime('20030201_040506', "%Y%m%d_%H%M%S")
    for release in releases:
        k = f"{URL_AUTOPKGTEST}/results/autopkgtest-{release}-{owner_name}-{ppa_name}/"
        fake_results[k] = []
        for arch in architectures:
            # We don't care about the triggers for the result, just the
            # number of results and their basic identity, so replace the
            # get_triggers() call to avoid it making any remote calls.
            result = Result(url=fake_data_url, time=timestamp, series=release, arch=arch, source=None)
            result.get_triggers = lambda: "x"
            fake_results[k].append(result)

    def fake_get_results(response, base_url, arches, sources):
        return fake_results[base_url]
    mock_get_results.side_effect = fake_get_results

    ppa = Ppa(ppa_name, owner_name)
    results = ppa.get_autopkgtest_results(releases, architectures)

    assert len(results) == expected_num_results
    for trigger_set in results:
        assert isinstance(trigger_set, dict)
        assert all(len(triggers) == expected_num_triggers for triggers in trigger_set.values())


@pytest.mark.parametrize('address, expected', [
    # Successful cases
    ('bb', (None, 'bb')),
    ('123', (None, '123')),
    ('a/123', ('a', '123')),
    ('ppa:A/bb', ('a', 'bb')),
    ('ppa:a/bb', ('a', 'bb')),
    ('ppa:ç/bb', ('ç', 'bb')),
    ('https://launchpad.net/~a/+archive/ubuntu/bb', ('a', 'bb')),
    ('https://launchpad.net/~a/+archive/ubuntu/bb/', ('a', 'bb')),
    ('https://launchpad.net/~a/+archive/ubuntu/bb////', ('a', 'bb')),
    ('https://launchpad.net/~a/+archive/ubuntu/bb/+packages', ('a', 'bb')),
    ('https://launchpad.net/~a/+archive/ubuntu/bb/+x', ('a', 'bb')),

    # Expected failure cases
    ('ppa:', (None, None)),
    (None, (None, None)),
    ('', (None, None)),
    ('/', (None, None)),
    (':/', (None, None)),
    ('////', (None, None)),
    ('ppa:/', (None, None)),
    ('ppa:a/', (None, None)),
    ('ppa:/bb', (None, None)),
    ('ppa:a/bç', (None, None)),
    ('ppa/a/bb', (None, None)),
    ('ppa:a/bb/c', (None, None)),
    ('ppa:a/bB', (None, None)),
    ('http://launchpad.net/~a/+archive/ubuntu/bb', (None, None)),
    ('https://example.com/~a/+archive/ubuntu/bb', (None, None)),
    ('https://launchpad.net/~a/+archive/nobuntu/bb', (None, None)),
    ('https://launchpad.net/~a/+archive/ubuntu/bb/x', (None, None)),
    ('https://launchpad.net/~a/+archive/ubuntu/bb/+', (None, None)),
])
def test_ppa_address_split(address, expected):
    """Check ppa address input strings can be parsed properly."""
    result = ppa_address_split(address)
    assert result == expected


def test_default_pocket():
    lp = LpServiceMock()
    ppa = PpaGroup(name='me', service=lp).create('foo')
    assert ppa.pocket == 'updates'


def test_set_pocket():
    lp = LpServiceMock()
    ppa = PpaGroup(name='me', service=lp).create('foo')
    ppa.set_pocket('proposed')
    assert ppa.pocket == 'proposed'


def test_set_pocket_error():
    lp = LpServiceMock()
    ppa = PpaGroup(name='me', service=lp).create('foo')
    with pytest.raises(ValueError):
        ppa.set_pocket('invalid-pocket')


def test_get_ppa():
    ppa = get_ppa(None, {'owner_name': 'a', 'ppa_name': 'bb'})
    assert type(ppa) is Ppa
    assert ppa.owner_name == 'a'
    assert ppa.ppa_name == 'bb'
