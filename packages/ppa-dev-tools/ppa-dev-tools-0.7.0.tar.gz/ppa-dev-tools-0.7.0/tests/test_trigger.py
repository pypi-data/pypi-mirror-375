#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2022-2024 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests the Trigger class for managing Autopkgtest trigger URLs."""

import os
import sys

import json
import pytest

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.trigger import Trigger, get_triggers, show_triggers
from ppa.source_publication import SourcePublication


def test_object():
    """Checks that Trigger objects can be instantiated."""
    trigger = Trigger(SourcePublication('x', 'x', 'x'), 'x')
    assert trigger


@pytest.mark.parametrize('pub, arch, test_pkg, expected_repr', [
    (
        SourcePublication('pkg', 'ver', 'ser'),
        'arch',
        'tst',
        (
            "Trigger(source_publication=SourcePublication("
            "package='pkg', version='ver', series='ser', archive=None, status=None), "
            "architecture='arch', "
            "test_package='tst')"
        )
    ),
    (
        SourcePublication('pkg', 'ver', 'ser'),
        'arch',
        None,
        (
            "Trigger(source_publication=SourcePublication("
            "package='pkg', version='ver', series='ser', archive=None, status=None), "
            "architecture='arch', "
            "test_package='pkg')"
        )
    ),
])
def test_repr(pub, arch, test_pkg, expected_repr):
    """Checks Trigger object representation."""
    trigger = Trigger(pub, arch, test_pkg)
    assert repr(trigger) == expected_repr


@pytest.mark.parametrize('pub, arch, test_pkg, expected_str', [
    (
        SourcePublication('pkg', 'ver', 'ser'),
        'arch',
        None,
        'pkg: ser/pkg/ver [arch]'
    ),
    (
        SourcePublication('pkg', 'ver', 'ser', 'ppa'),
        'arch',
        None,
        'pkg: ser/pkg/ver (ppa) [arch]'
    ),
    (
        SourcePublication('dovecot', '1:2.3.19.1+dfsg1-2ubuntu2', 'kinetic', None),
        'armhf',
        'apache2',
        'apache2: kinetic/dovecot/1:2.3.19.1+dfsg1-2ubuntu2 [armhf]'
    ),
])
def test_str(pub, arch, test_pkg, expected_str):
    """Checks Trigger object textual presentation."""
    trigger = Trigger(pub, arch, test_pkg)
    assert f"{trigger}" == expected_str


def test_to_dict():
    """Checks Trigger object structural representation."""
    trigger = Trigger(SourcePublication('x', 'x', 'x', 'x'), 'x', 'x')
    expected_keys = [
        'architecture', 'source_publication', 'test_package',
    ]
    expected_types = [str, dict]

    d = trigger.to_dict()
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


@pytest.mark.parametrize('pub, arch, test_pkg, expected', [
    (
        SourcePublication('pkg', 'ver', 'ser'),
        'arch',
        None,
        "/request.cgi?release=ser&package=pkg&arch=arch&trigger=pkg%2Fver"
    ),
    (
        SourcePublication('p', 'v', 's', 'ppa:a/b'),
        'a',
        None,
        "/request.cgi?release=s&package=p&arch=a&trigger=p%2Fv&ppa=ppa%3Aa%2Fb"
    ),
    (
        SourcePublication('p', '1.2+git345', 's'),
        'a',
        None,
        "/request.cgi?release=s&package=p&arch=a&trigger=p%2F1.2%2Bgit345"
    ),
    (
        SourcePublication('apache2', '2.4', 'kinetic'),
        'a',
        'pkg',
        "/request.cgi?release=kinetic&package=pkg&arch=a&trigger=apache2%2F2.4"
    )
])
def test_action_url(pub, arch, test_pkg, expected):
    """Checks that Trigger objects generate valid autopkgtest action urls."""
    trigger = Trigger(pub, arch, test_pkg)
    assert expected in trigger.action_url


@pytest.mark.parametrize('params, expected', [
    (
        ['pkg', 'ver', None, 'ser', [], None],
        [],
    ),
    (
        ['pkg', 'ver', None, 'ser', ['arch'], 'tst'],
        [
            Trigger(SourcePublication('pkg', 'ver', 'ser'), 'arch', 'tst'),
        ],
    ),
    (
        ['pkg', 'ver', 'ppa', 'ser', ['ax', 'ay', 'az'], 'tst'],
        [
            Trigger(SourcePublication('pkg', 'ver', 'ser', 'ppa'), 'ax', 'tst'),
            Trigger(SourcePublication('pkg', 'ver', 'ser', 'ppa'), 'ay', 'tst'),
            Trigger(SourcePublication('pkg', 'ver', 'ser', 'ppa'), 'az', 'tst'),
        ],
    ),
])
def test_get_triggers(params, expected):
    """Checks that Trigger objects get generated properly from inputs."""
    for trigger in get_triggers(*params):
        assert repr(trigger) in [repr(t) for t in expected]


@pytest.mark.parametrize('triggers, params, expected_in_stdout', [
    (
        # Basic function parameters, no triggers
        [],
        {},
        [""]
    ),
    (
        # Specified trigger (clickable)
        [Trigger(SourcePublication('p', 'v', 's', 'ppa'), 'a')],
        {'show_trigger_urls': False},
        [
            "&trigger=p%2Fv&ppa=ppa\x1b\\Trigger basic @a♻️ \x1b]8;;\x1b",
            "&trigger=p%2Fv&ppa=ppa&all-proposed=1\x1b\\Trigger all-proposed @a💍\x1b]8;;\x1b\\\n"
        ]
    ),
    (
        # Specified trigger (display plain URLs)
        [Trigger(SourcePublication('pkg', '123', 'x-series', 'y-ppa'), 'i386')],
        {'show_trigger_urls': True},
        [
            "&trigger=pkg%2F123&ppa=y-ppa ♻️ \n",
            "&trigger=pkg%2F123&ppa=y-ppa&all-proposed=1 💍\n"
        ]
    ),
    (
        # Display names of packages in trigger lines
        [Trigger(SourcePublication('pkg', '123', 'x-series'), 'i386')],
        {'show_trigger_names': True},
        ["Trigger basic pkg@i386♻️ ", "Trigger all-proposed pkg@i386💍"]
    ),
    (
        # Omit package names if specified
        [Trigger(SourcePublication('pkg', '123', 'x-series'), 'i386')],
        {'show_trigger_names': False},
        ["Trigger basic @i386", "Trigger all-proposed @i386"]
    ),
    (
        # Display names of packages in trigger lines when trigger URLs are shown
        [Trigger(SourcePublication('pkg', '123', 'x-series'), 'i386')],
        {'show_trigger_urls': True, 'show_trigger_names': True},
        ["pkg@i386: https:", "trigger=pkg%2F123"]
    ),
    (
        # Multiple triggers
        [
            Trigger(SourcePublication('pkg', '123', 'x-series'), 'i386'),
            Trigger(SourcePublication('lib', '321', 'x-series'), 'i386')
        ],
        {'show_trigger_urls': True},
        ["trigger=pkg%2F123", "trigger=lib%2F321"]
    ),
])
def test_show_triggers(capfd, triggers, params, expected_in_stdout):
    """Check that trigger strings are included in generated output."""
    params.setdefault('triggers', [])
    for t in triggers:
        params['triggers'].append(t)
    show_triggers(**params)
    out, _ = capfd.readouterr()
    print(out)
    for text in expected_in_stdout:
        assert text in out
