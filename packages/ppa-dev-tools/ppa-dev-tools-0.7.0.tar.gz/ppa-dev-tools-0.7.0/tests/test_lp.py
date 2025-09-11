#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# Copyright (C) 2019-2020 Bryce Harrington <bryce@canonical.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# pylint: disable=W0212

"""Tests the Launchpad class as an interface to the Launchpad service API.

Tests for our launchpadlib wrapper & helper methods.
"""

import sys
import os.path
from unittest.mock import Mock, patch

import logging
import pytest
from launchpadlib.launchpad import Launchpad

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.lp import Lp

APPNAME = 'test-lp'


@pytest.fixture(name='fakelp')
def fixture_fakelp():
    """Connect to Launchpad."""
    mock_launchpad = Mock(spec=Launchpad)

    return Lp(
        application_name=APPNAME,
        service=mock_launchpad)


def test_new_connection():
    """Verifies the Lp object will auto-login properly."""
    mock_launchpad = Mock(spec=Launchpad)

    lp = Lp(
        application_name=APPNAME,
        service=mock_launchpad)

    # Cause the lp._instance() internal property to be triggered
    logging.debug(lp.me)
    logging.debug(lp.people)

    # Verify the triggering resulted in a login attempt
    mock_launchpad.login_with.assert_called_once_with(
        application_name=APPNAME,
        service_root='production',
        allow_access_levels=['WRITE_PRIVATE'],
        version='devel',
    )


@patch("ppa.lp.Credentials")
def test_new_connection_creds(credentials_mock):
    """Verifies the Lp object will login if credentials are provided."""
    mock_launchpad = Mock(spec=Launchpad)

    lp = Lp(
        application_name=APPNAME,
        service=mock_launchpad,
        credentials='...')

    # Cause the lp._instance() internal property to be triggered
    logging.debug(lp.me)
    logging.debug(lp.people)

    # Verify the triggering did not result in a login attempt
    mock_launchpad.login_with.assert_not_called()
    # Rather that the login was done via envvar
    # creating the credentials
    credentials_mock.from_string.assert_called_once()
    # and the service was created with the given credentials
    mock_launchpad.assert_called_once_with(
        credentials_mock.from_string.return_value,
        None,
        None,
        service_root="production",
        version="devel"
    )


def test_api_root(fakelp):
    """Ensures we can get LP's API root."""
    fakelp.load(Lp.API_ROOT_URL + 'hi')
    fakelp._instance.load.assert_called_once_with(
        'https://api.launchpad.net/devel/hi')


def test_ubuntu(fakelp):
    """Checks the .ubuntu property."""
    fakelp._instance.distributions = {'ubuntu': 'UBUNTU'}
    assert fakelp.ubuntu == 'UBUNTU'


def test_ubuntu_active_series(fakelp):
    """Checks the active series names for Ubuntu."""
    mock_hirsute = Mock(active=False)
    mock_hirsute.name = 'hirsute'

    mock_jammy = Mock(active=True)
    mock_jammy.name = 'jammy'

    mock_ubuntu = Mock(series=[mock_hirsute, mock_jammy])
    fakelp._instance.distributions = {'ubuntu': mock_ubuntu}
    assert fakelp.ubuntu_active_series()[0] == mock_jammy
    assert fakelp.ubuntu_active_series()[0].name == 'jammy'


def test_ubuntu_devel_series(fakelp):
    """Checks the devel series name for Ubuntu."""
    mock_mantic = Mock(active=False)
    mock_mantic.name = 'mantic'

    mock_jammy = Mock(active=True)
    mock_jammy.name = 'jammy'

    mock_ubuntu = Mock(series=[mock_mantic, mock_jammy])
    mock_ubuntu.getDevelopmentSeries.return_value = [mock_mantic]
    fakelp._instance.distributions = {'ubuntu': mock_ubuntu}
    assert fakelp.ubuntu_devel_series() == [mock_mantic]
    assert fakelp.ubuntu_devel_series()[0].name == 'mantic'


def test_ubuntu_stable_series(fakelp):
    """Checks the stable series name for Ubuntu."""
    mock_hirsute = Mock(active=False)
    mock_hirsute.name = 'hirsute'

    mock_jammy = Mock(status='Supported')
    mock_jammy.name = 'jammy'

    mock_kinetic = Mock(status='Obsolete')
    mock_kinetic.name = 'kinetic'

    mock_lunar = Mock(status='Current Stable Release')
    mock_lunar.name = 'lunar'

    mock_mantic = Mock(status='Active Development')
    mock_mantic.name = 'mantic'

    mock_mantic = Mock(status='Future')
    mock_mantic.name = 'nseries'

    mock_ubuntu = Mock(series=[mock_hirsute, mock_jammy, mock_kinetic, mock_lunar, mock_mantic])
    fakelp._instance.distributions = {'ubuntu': mock_ubuntu}
    assert fakelp.ubuntu_stable_series() == [mock_lunar]


def test_debian(fakelp):
    """Checks the .debian property."""
    fakelp._instance.distributions = {'debian': 'DEBIAN'}
    assert fakelp.debian == 'DEBIAN'


def test_debian_active_series(fakelp):
    """Checks the active series names for Debian."""
    mock_woody = Mock(active=False)
    mock_woody.name = 'woody'

    mock_buster = Mock(active=True)
    mock_buster.name = 'buster'

    mock_sid = Mock(active=False)
    mock_sid.name = 'experimental'

    mock_debian = Mock(series=[mock_woody, mock_buster, mock_sid])
    fakelp._instance.distributions = {'debian': mock_debian}
    assert fakelp.debian_active_series()[0].name == 'buster'


def test_debian_experimental_series(fakelp):
    """Checks the experimental series name for Debian."""
    mock_woody = Mock(active=False)
    mock_woody.name = 'woody'

    mock_buster = Mock(active=True)
    mock_buster.name = 'buster'

    mock_sid = Mock(active=False)
    mock_sid.name = 'experimental'

    mock_debian = Mock(series=[mock_woody, mock_buster, mock_sid])
    fakelp._instance.distributions = {'debian': mock_debian}
    assert fakelp.debian_experimental_series() == mock_sid


def test_get_teams(fakelp):
    """Checks that a person's teams can be retrieved."""
    mock_me = Mock(memberships_details=[
        Mock(name='t1', self_link="https://launchpad.net/~t1"),
        Mock(name='t2', self_link="https://launchpad.net/~t2/+blah"),
        Mock(name='t3', self_link="https://launchpad.net/~t3/+blah"),
    ])
    fakelp._instance.people = {'me': mock_me}
    assert fakelp.get_teams('me') == ['t1', 't2', 't3']
