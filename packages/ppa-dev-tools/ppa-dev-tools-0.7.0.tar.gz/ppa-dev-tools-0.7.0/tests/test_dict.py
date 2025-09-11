#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2023 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests helper routines for handling dict objects."""

import os
import sys
import pytest

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.dict import unpack_to_dict


@pytest.mark.parametrize('text, expected', [
    ('a',                 {'a': ''}),
    ('a=1',               {'a': '1'}),
    ('a=1:2',             {'a': '1:2'}),
    ('a = 1',             {'a': '1'}),
    ('a:x',               {'a': ''}),
    ('a:x:',              {'a': ''}),
    ('a:x:y',             {'a': ''}),
    ('a:x=1',             {'a': '1'}),
    ('a:x = 1',           {'a': '1'}),
    ('a=x=1',             {'a': 'x=1'}),
    ('a : x=1',           {'a': '1'}),
    ('a,b',               {'a': '', 'b': ''}),
    ('a, b',              {'a': '', 'b': ''}),
    ('a,b=1.2.3,c:x=4',   {'a': '', 'b': '1.2.3', 'c': '4'}),
    ('a, b=1.2.3, c:x=4', {'a': '', 'b': '1.2.3', 'c': '4'}),
    ('a, b|c',            {'a': '', ('b', 'c'): {'b': '', 'c': ''}}),
    ('a, b=1|c=2',        {'a': '', ('b', 'c'): {'b': '1', 'c': '2'}}),
    ('a, b=1|c:x=2, d=3', {'a': '', ('b', 'c'): {'b': '1', 'c': '2'}, 'd': '3'}),
])
def test_unpack_to_dict(text, expected):
    """Checks the unpack_to_dict() routine's string unpacking."""
    result = unpack_to_dict(text)

    assert result
    assert isinstance(result, dict)
    assert result == expected


@pytest.mark.parametrize('text, expected_exception', [
    (None, ValueError),
    ('',   ValueError),
    (',',  ValueError),
    (',z', ValueError),
    (':',  ValueError),
    (':z', ValueError),
    ('=',  ValueError),
    ('=z', ValueError),
])
def test_unpack_to_dict_error(text, expected_exception):
    """Checks the unpack_to_dict() routine's string unpacking."""
    with pytest.raises(expected_exception):
        unpack_to_dict(text)


@pytest.mark.parametrize('text, key_cut, sep, expected', [
    ('a:x=1', ':',  '=',  {'a': '1'}),

    ('a.x=1', '.',  '=',  {'a': '1'}),
    ('a+x=1', '+',  '=',  {'a': '1'}),
    ('a-x=1', '-',  '=',  {'a': '1'}),
    ('a~x=1', '~',  '=',  {'a': '1'}),
    ('a_x=1', '_',  '=',  {'a': '1'}),
    ('a!x=1', '!',  '=',  {'a': '1'}),
    ('a;x=1', ';',  '=',  {'a': '1'}),
    ('a/x=1', '/',  '=',  {'a': '1'}),

    ('a:x.1', ':',  '.',  {'a': '1'}),
    ('a:x+1', ':',  '+',  {'a': '1'}),
    ('a:x-1', ':',  '-',  {'a': '1'}),
    ('a:x~1', ':',  '~',  {'a': '1'}),
    ('a:x_1', ':',  '_',  {'a': '1'}),
    ('a:x!1', ':',  '!',  {'a': '1'}),
    ('a:x;1', ':',  ';',  {'a': '1'}),
    ('a:x/1', ':',  '/',  {'a': '1'}),

    # Spaces are allowed as separators
    ('a 1', ':', ' ', {'a': '1'}),
    ('a 1, b, c 3', ':', ' ', {'a': '1', 'b': '', 'c': '3'}),

])
def test_unpack_to_dict_parameters(text, sep, key_cut, expected):
    """Checks the unpack_to_dict() routine's string unpacking."""
    result = unpack_to_dict(text, key_sep=sep, key_cut=key_cut)

    assert result
    assert isinstance(result, dict)
    assert result == expected


@pytest.mark.parametrize('text, key_cut, sep, expected_exception', [
    # Commas are reserved as the item separator
    ('a:x=1', ',',  '=',  ValueError),
    ('a:x=1', ':',  ',',  ValueError),
    ('a:x=1', ',',  ',',  ValueError),

    # key_cut and sep have to be different
    ('a:x=1', ':',  ':', ValueError),
    ('a:x=1', '=',  '=', ValueError),
    ('a:x=1', '.',  '.', ValueError),
])
def test_unpack_to_dict_parameters_error(text, sep, key_cut, expected_exception):
    """Checks the unpack_to_dict() error handling, with invalid parameters."""
    with pytest.raises(expected_exception):
        unpack_to_dict(text, key_sep=sep, key_cut=key_cut)
