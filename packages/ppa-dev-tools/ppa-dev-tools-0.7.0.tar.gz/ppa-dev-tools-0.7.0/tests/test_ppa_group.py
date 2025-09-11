#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2019 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests the PpaGroup class as a way to manage a Team or Person's PPAs."""

import os
import sys

import pytest

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.ppa_group import PpaGroup, PpaAlreadyExists
from tests.helpers import LpServiceMock


def test_object():
    """Checks that PpaGroup objects can be instantiated."""
    ppa_group = PpaGroup(service=LpServiceMock(), name='test-ppa')
    assert ppa_group

    with pytest.raises(ValueError):
        ppa_group = PpaGroup(service=LpServiceMock(), name=None)
    with pytest.raises(ValueError):
        ppa_group = PpaGroup(service=None, name='test-ppa')


def test_create_ppa():
    """Checks that PpaGroups can create PPAs."""
    name = 'test_ppa'
    ppa_group = PpaGroup(service=LpServiceMock(), name='me')
    ppa = ppa_group.create(name)
    assert ppa is not None
    assert name in ppa.address
    assert type(ppa.description) is str


def test_create_existing_ppa():
    """Check exception creating an already created PPA."""
    name = 'test_ppa'
    ppa_group = PpaGroup(service=LpServiceMock(), name='me')
    ppa_group.create(name)
    with pytest.raises(PpaAlreadyExists):
        ppa_group.create(name)


def test_create_with_description():
    """Check setting a description for a PPA."""
    ppa_group = PpaGroup(service=LpServiceMock(), name='me')
    description = 'PPA Test Description'
    ppa = ppa_group.create('test_ppa_with_description', description)
    assert ppa is not None
    assert ppa.description == description


def test_create_with_owner():
    """Check creating a PPA for a particular owner."""
    lp = LpServiceMock()
    lp.launchpad.add_person('test_owner_name')
    ppa_group = PpaGroup(service=lp, name='test_owner_name')
    ppa = ppa_group.create('ppa_test_name')
    assert ppa is not None
    assert ppa.address == 'ppa:test_owner_name/ppa_test_name'


def test_create_private():
    """Check creating a private PPA."""
    lp = LpServiceMock()
    ppa_group = PpaGroup(service=lp, name='me')
    ppa = ppa_group.create('private_ppa', private=True)
    assert ppa is not None
    assert ppa.address == 'ppa:me/private_ppa'
    assert ppa.is_private is True


def test_list_ppas():
    """Check listing the PPAs for a PPA group."""
    test_ppa_list = ['a', 'b', 'c', 'd']
    ppa_group = PpaGroup(service=LpServiceMock(), name='me')

    # Add several ppas
    for ppa in test_ppa_list:
        ppa_group.create(ppa)

    ppas = [ppa.name for ppa in list(ppa_group.ppas)]
    assert test_ppa_list == ppas
