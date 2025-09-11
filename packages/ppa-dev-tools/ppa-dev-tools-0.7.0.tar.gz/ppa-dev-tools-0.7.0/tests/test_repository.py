#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2023 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests the Repository class as an interface to an Apt repository."""

import os
import sys

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.repository import Repository
from ppa.suite import Suite


def test_object(tmp_path):
    """Checks that Repository objects can be instantiated."""
    repository = Repository(tmp_path)
    assert repository


def test_suites(tmp_path):
    """Checks getting all suites from the repository."""
    suites = ['a', 'b', 'b-0', 'b-1']
    for suite in suites:
        suite_dir = tmp_path / suite
        suite_dir.mkdir()

    repository = Repository(tmp_path)
    assert sorted(repository.suites.keys()) == sorted(suites)
    for suite in repository.suites.values():
        assert isinstance(suite, Suite)


def test_get_suite(tmp_path):
    """Checks getting a specific suite from the repository."""
    suites = ['a', 'b', 'b-0', 'b-1']
    for suite in suites:
        suite_dir = tmp_path / suite
        suite_dir.mkdir()

    repository = Repository(tmp_path)
    suite = repository.get_suite('b', '1')
    assert suite
    assert str(suite) == 'b-1'
