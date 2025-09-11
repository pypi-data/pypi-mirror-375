#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2021 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests the ppa command-line script."""

import os
import io
import sys
import types

import importlib.machinery
import argparse
from unittest.mock import patch

import pytest

SCRIPT_NAME = "ppa"
BASE_PATH = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
sys.path.insert(0, BASE_PATH)

from ppa.ppa import Ppa
from ppa.constants import (
    ARCHES_PPA_ALL,
    ARCHES_PPA_DEFAULT
)
from tests.helpers import (
    LpServiceMock,
    PublicationMock
)

if '.pybuild' in BASE_PATH:
    # pylint: disable-next=invalid-name
    python_version = '.'.join([str(v) for v in sys.version_info[0:2]])
    scripts_path = os.path.join(
        BASE_PATH.replace(f'/.pybuild/cpython3_{python_version}/', '/'),
        f'scripts-{python_version}'
    )
else:
    scripts_path = os.path.join(BASE_PATH, 'scripts')

script_path = os.path.join(scripts_path, SCRIPT_NAME)
loader = importlib.machinery.SourceFileLoader(SCRIPT_NAME, script_path)
script = types.ModuleType(loader.name)
loader.exec_module(script)


@pytest.fixture
def fake_config():
    return {
        'ppa_name': 'testing',
        'owner_name': 'me',
        'wait_seconds': 0.1,
        'quiet': True
    }


@pytest.fixture
def fake_source_package():
    # TODO: Implement
    return {
        'name': 'test-source',
        'version': '1.0-2ubuntu3',
        'binaries': [
            {'name': 'foo'},
            {'name': 'bar'}
        ]
    }


@pytest.fixture
def fake_binary_package():
    # TODO: Implement
    return {
        'name': 'test-binary',
        'source': 'test-source',
    }


@pytest.fixture
def fake_build():
    # TODO: Implement, including build errors
    return {
        'binary': 'foo',
        'status': 'Failed',
    }


@pytest.fixture
def fake_bug_report():
    # TODO: Implement
    return {
        'id': 1234,
        'title': 'foobar',
        'desc': 'baz',
    }


def test_create_arg_parser():
    """
    Checks that the main argument processor is created properly.
    It must support the top level options as well as the expected
    set of subparsers.

    Note we don't test --help or --version since these are built-ins
    from argparse so we don't control their behavior.  They also both
    exit when done which is not conducive to testing.
    """
    parser = script.create_arg_parser()

    # Check command is recognized
    args = parser.parse_args(['show', 'test-ppa'])
    assert args.command == 'show'

    # Check -A, --credentials
    args = parser.parse_args(['-A', 'my-creds', 'show', 'test-ppa'])
    assert args.credentials_filename == "my-creds"
    args.credentials_filename = None
    args = parser.parse_args(['--credentials', 'my-creds', 'show', 'test-ppa'])
    assert args.credentials_filename == "my-creds"
    args.credentials_filename = None

    # Check -D, --debug
    args = parser.parse_args(['-D', 'show', 'test-ppa'])
    assert args.debug is True
    args.debug = None
    args = parser.parse_args(['--debug', 'show', 'test-ppa'])
    assert args.debug is True
    args.debug = None

    # Check -q, --dry-run
    args = parser.parse_args(['--dry-run', 'show', 'test-ppa'])
    assert args.dry_run is True
    args.dry_run = None

    # Check -v, --verbose
    args = parser.parse_args(['-v', 'show', 'test-ppa'])
    assert args.verbose is True
    args.verbose = None
    args = parser.parse_args(['--verbose', 'show', 'test-ppa'])
    assert args.verbose is True
    args.verbose = None

    # Check -q, --quiet
    args = parser.parse_args(['-q', 'show', 'test-ppa'])
    assert args.quiet is True
    args.quiet = None
    args = parser.parse_args(['--quiet', 'show', 'test-ppa'])
    assert args.quiet is True
    args.quiet = None

    # Verify all expected subparsers are present
    subparsers_actions = [
        action for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)]
    subparsers = []
    for subparsers_action in subparsers_actions:
        for choice, _ in subparsers_action.choices.items():
            subparsers.append(choice)
    assert subparsers == [
        'create',
        'credentials',
        'desc',
        'destroy',
        'list',
        'set',
        'show',
        'tests',
        'wait'
    ]


@pytest.mark.parametrize('command', ['create', 'set'])
def test_create_arg_parser_basic_config(command):
    """Checks argument parsing for the basic PPA config options.

    This test covers the set of options used by 'create' and 'set' for
    configuring various properties of the PPA's behaviors, such as
    dependencies, publication policy, access control, etc.  It does not
    cover settings that require Launchpad administrator involvement.

    The testing checks only that the options are being received and
    registered as expected, and does not cover the processing of the
    inputs nor the actual underlying functionality.
    """
    parser = script.create_arg_parser()

    # Check command and ppa_name
    args = parser.parse_args([command, 'test-ppa'])
    assert args.command == command
    assert args.ppa_name == 'test-ppa'

    # Check that command args can come before or after the ppa name
    args = parser.parse_args([command, 'test-ppa', '-a', 'x'])
    assert args.architectures == 'x'
    args.architectures = None
    args = parser.parse_args([command, '-a', 'x', 'test-ppa'])
    assert args.architectures == 'x'
    args.architectures = None

    # Check --all-arches and --default-arches
    args = parser.parse_args([command, 'test-ppa', '--all-arches'])
    assert args.architectures == ','.join(ARCHES_PPA_ALL)
    args.architectures = None
    args = parser.parse_args([command, 'test-ppa', '--all-architectures'])
    assert args.architectures == ','.join(ARCHES_PPA_ALL)
    args.architectures = None
    args = parser.parse_args([command, 'test-ppa', '--default-arches'])
    assert args.architectures == ','.join(ARCHES_PPA_DEFAULT)
    args.architectures = None
    args = parser.parse_args([command, 'test-ppa', '--default-architectures'])
    assert args.architectures == ','.join(ARCHES_PPA_DEFAULT)
    args.architectures = None

    # Check -a, --arch, --arches, --architectures
    args = parser.parse_args([command, 'test-ppa', '-a', 'x'])
    assert args.architectures == 'x'
    args.architectures = None
    args = parser.parse_args([command, 'test-ppa', '--arch', 'x'])
    assert args.architectures == 'x'
    args.architectures = None
    args = parser.parse_args([command, 'test-ppa', '--arches', 'x'])
    assert args.architectures == 'x'
    args.architectures = None
    args = parser.parse_args([command, 'test-ppa', '--architectures', 'a,b,c'])
    assert args.architectures == 'a,b,c'
    args.architectures = None

    # Check --displayname
    args = parser.parse_args([command, 'test-ppa', '--displayname', 'x'])
    assert args.displayname == 'x'
    args.displayname = None

    # Check --description
    args = parser.parse_args([command, 'test-ppa', '--description', 'x'])
    assert args.description == 'x'
    args.description = None

    # Check --public / -P|--private
    args = parser.parse_args([command, 'test-ppa', '--public'])
    assert args.private is False
    args.public = None
    args = parser.parse_args([command, 'test-ppa', '--private'])
    assert args.private is True
    args.private = None
    args = parser.parse_args([command, 'test-ppa', '-P'])
    assert args.private is True
    args.private = None

    # Check --ppa-dependencies <PPA[,...]>
    args = parser.parse_args([command, 'test-ppa', '--ppa-dependencies', 'a,b,c'])
    assert args.ppa_dependencies == "a,b,c"
    args.ppa_dependencies = None
    args = parser.parse_args([command, 'test-ppa', '--ppa-depends', 'a,b,c'])
    assert args.ppa_dependencies == "a,b,c"
    args.ppa_dependencies = None

    # Check --publish
    args = parser.parse_args([command, 'test-ppa', '--publish'])
    assert args.publish is True
    args.publish = None
    args = parser.parse_args([command, 'test-ppa', '--no-publish'])
    assert args.publish is False
    args.publish = None


def test_create_arg_parser_create():
    """Checks argument parsing for the 'create' command.

    Most of the create command's args are covered by
    test_create_arg_parser_basic_config(), this just verifies
    the few that aren't.
    """
    parser = script.create_arg_parser()
    command = 'create'

    # Check ppa_name
    args = parser.parse_args([command, 'test-ppa'])
    assert args.ppa_name == 'test-ppa'
    args = parser.parse_args([command, 'my-team/test-ppa'])
    assert args.ppa_name == 'my-team/test-ppa'
    args = parser.parse_args([command, 'ppa:my-team/test-ppa'])
    assert args.ppa_name == 'ppa:my-team/test-ppa'

    # Check --owner, --owner-name, --team, --team-name
    args = parser.parse_args([command, 'test-ppa', '--owner', 'x'])
    assert args.owner_name == 'x'
    args.owner_name = None
    args = parser.parse_args([command, 'test-ppa', '--owner-name', 'x'])
    assert args.owner_name == 'x'
    args.owner_name = None
    args = parser.parse_args([command, 'test-ppa', '--team', 'x'])
    assert args.owner_name == 'x'
    args.owner_name = None
    args = parser.parse_args([command, 'test-ppa', '--team-name', 'x'])
    assert args.owner_name == 'x'
    args.owner_name = None

    # Check --pocket
    args = parser.parse_args([command, 'test-ppa', '--pocket', 'proposed'])
    assert args.pocket == "proposed"
    args.pocket = None


def test_create_arg_parser_show():
    """Checks argument parsing for the 'show' command."""
    parser = script.create_arg_parser()
    command = 'show'

    # Check ppa_name
    args = parser.parse_args([command, 'test-ppa'])
    assert args.ppa_name == 'test-ppa'

    # Check -a, --arch, --arches, --architectures
    args = parser.parse_args([command, 'test-ppa', '-a', 'x'])
    assert args.architectures == 'x'
    args.architectures = None

    args = parser.parse_args([command, 'test-ppa', '--arch', 'x'])
    assert args.architectures == 'x'
    args.architectures = None
    args = parser.parse_args([command, 'test-ppa', '--arches', 'x'])
    assert args.architectures == 'x'
    args.architectures = None
    args = parser.parse_args([command, 'test-ppa', '--architectures', 'a,b,c'])
    assert args.architectures == 'a,b,c'
    args.architectures = None

    # Check -r, --release, --releases
    args = parser.parse_args([command, 'test-ppa', '-r', 'x'])
    assert args.releases == 'x'
    args.releases = None
    args = parser.parse_args([command, 'test-ppa', '--release', 'x'])
    assert args.releases == 'x'
    args.releases = None
    args = parser.parse_args([command, 'test-ppa', '--releases', 'x'])
    assert args.releases == 'x'
    args.releases = None
    args = parser.parse_args([command, 'test-ppa', '--releases', 'x,y,z'])
    assert args.releases == 'x,y,z'
    args.releases = None

    # Check -p, --package, --packages
    args = parser.parse_args([command, 'tests-ppa', '-p', 'x'])
    assert args.packages == 'x'
    args.packages = None
    args = parser.parse_args([command, 'tests-ppa', '--package', 'x'])
    assert args.packages == 'x'
    args.packages = None
    args = parser.parse_args([command, 'tests-ppa', '--packages', 'x'])
    assert args.packages == 'x'
    args.packages = None
    args = parser.parse_args([command, 'tests-ppa', '--packages', 'x,y,z'])
    assert args.packages == 'x,y,z'
    args.packages = None


def test_create_arg_parser_tests():
    """Checks argument parsing for the 'tests' command."""
    parser = script.create_arg_parser()
    command = 'tests'

    # Check ppa_name
    args = parser.parse_args([command, 'test-ppa'])
    assert args.ppa_name == 'test-ppa'

    # Check -a, --arch, --arches, --architectures
    args = parser.parse_args([command, 'test-ppa', '-a', 'x'])
    assert args.architectures == 'x'
    args.architectures = None

    args = parser.parse_args([command, 'test-ppa', '--arch', 'x'])
    assert args.architectures == 'x'
    args.architectures = None
    args = parser.parse_args([command, 'test-ppa', '--arches', 'x'])
    assert args.architectures == 'x'
    args.architectures = None
    args = parser.parse_args([command, 'test-ppa', '--architectures', 'a,b,c'])
    assert args.architectures == 'a,b,c'
    args.architectures = None

    # Check -r, --release, --releases
    args = parser.parse_args([command, 'test-ppa', '-r', 'x'])
    assert args.releases == 'x'
    args.releases = None
    args = parser.parse_args([command, 'test-ppa', '--release', 'x'])
    assert args.releases == 'x'
    args.releases = None
    args = parser.parse_args([command, 'test-ppa', '--releases', 'x'])
    assert args.releases == 'x'
    args.releases = None
    args = parser.parse_args([command, 'test-ppa', '--releases', 'x,y,z'])
    assert args.releases == 'x,y,z'
    args.releases = None

    # Check -p, --package, --packages
    args = parser.parse_args([command, 'tests-ppa', '-p', 'x'])
    assert args.packages == 'x'
    args.packages = None
    args = parser.parse_args([command, 'tests-ppa', '--package', 'x'])
    assert args.packages == 'x'
    args.packages = None
    args = parser.parse_args([command, 'tests-ppa', '--packages', 'x'])
    assert args.packages == 'x'
    args.packages = None
    args = parser.parse_args([command, 'tests-ppa', '--packages', 'x,y,z'])
    assert args.packages == 'x,y,z'
    args.packages = None

    # Check --show-urls, --show-url, -L
    args = parser.parse_args([command, 'tests-ppa'])
    assert args.show_urls is None
    args.show_urls = None
    args = parser.parse_args([command, 'tests-ppa', '--show-urls'])
    assert args.show_urls is True
    args.show_urls = None
    args = parser.parse_args([command, 'tests-ppa', '--show-url'])
    assert args.show_urls is True
    args.show_urls = None
    args = parser.parse_args([command, 'tests-ppa', '-L'])
    assert args.show_urls is True
    args.show_urls = None

    # Check --show-rdepends
    args = parser.parse_args([command, 'tests-ppa'])
    assert args.show_rdepends is None
    args.show_rdepends = None
    args = parser.parse_args([command, 'tests-ppa', '--show-rdepends'])
    assert args.show_rdepends is True
    args.show_rdepends = None


def test_create_arg_parser_wait():
    """Checks argument parsing for the 'wait' command."""
    parser = script.create_arg_parser()
    command = "wait"

    # Check ppa_name
    args = parser.parse_args([command, 'test-ppa'])
    assert args.ppa_name == 'test-ppa'

    # Check -l, --log
    args = parser.parse_args([command, 'test-ppa'])
    assert args.wait_logging is None
    args = parser.parse_args([command, 'test-ppa', '-l'])
    assert args.wait_logging is True
    args = parser.parse_args([command, 'test-ppa', '--log'])
    assert args.wait_logging is True


@pytest.mark.parametrize('command_line_options, expected_config', [
    pytest.param([], {}),
    (['show', 'ppa:aa/bb'], {'command': 'show', 'owner_name': 'aa', 'ppa_name': 'bb'}),
    (['show', 'aa/bb'], {'owner_name': 'aa', 'ppa_name': 'bb'}),
    (['show', 'bb'], {'owner_name': 'me', 'ppa_name': 'bb'}),
    (['--debug', 'show', 'ppa:aa/bb'], {'debug': True}),
    (['--dry-run', 'show', 'ppa:aa/bb'], {'dry_run': True}),
    (['--verbose', 'show', 'ppa:aa/bb'], {'verbose': True}),
    (['--quiet', 'show', 'ppa:aa/bb'], {'quiet': True}),
    (['create', 'ppa:aa/bb'], {'command': 'create', 'owner_name': 'aa', 'ppa_name': 'bb'}),
    (['create', 'aa/bb'], {'command': 'create', 'owner_name': 'aa', 'ppa_name': 'bb'}),
    (['create', 'bb', '--owner', 'aa'], {'command': 'create', 'owner_name': 'aa', 'ppa_name': 'bb'}),
    (['create', 'bb', '--owner-name', 'aa'], {'command': 'create', 'owner_name': 'aa', 'ppa_name': 'bb'}),
    (['create', 'bb', '--private'], {'command': 'create', 'private': True}),
    (['create', 'bb', '--public'], {'command': 'create', 'private': False}),
    (['create', 'bb', '--team', 'aa'], {'command': 'create', 'owner_name': 'aa', 'ppa_name': 'bb'}),
    (['create', 'bb', '--team-name', 'aa'], {'command': 'create', 'owner_name': 'aa', 'ppa_name': 'bb'}),
    ])
def test_create_config_from_args(command_line_options, expected_config):
    '''Checks creation of a config object from an argparser object.

    Prior tests cover the creation of proper args from the command line;
    this test relies on the already-tested argparse machinery to create
    various args to pass to create_config() in order to assure that the
    right config dict is generated in response.
    '''
    lp = LpServiceMock()
    parser = script.create_arg_parser()
    args = parser.parse_args(command_line_options)
    config = script.create_config(lp, args)

    for key, value in expected_config.items():
        assert key in config.keys()
        assert config[key] == value


@pytest.mark.parametrize('args, expected_exception', [
    # Bad command
    ([None], SystemExit),
    ([''], SystemExit),
    (['INVALID'], SystemExit),
    ([1], TypeError),

    # Bad ppa name
    (['show'], SystemExit),
    (['show', None], ValueError),
    (['show', ''], ValueError),
    (['show', 'INVALID'], ValueError),
    (['show', 1], TypeError),

    # Bad argument name
    (['--invalid', 'show', 'ppa:aa/bb'], SystemExit),
    ])
def test_create_config_from_args_error(args, expected_exception):
    '''Checks creation of a config object from an argparser object.'''
    lp = LpServiceMock()
    parser = script.create_arg_parser()

    with pytest.raises(expected_exception):
        args = parser.parse_args(args)
        script.create_config(lp, args)


@pytest.mark.parametrize('config, expected_config', [
    ({}, {}),
    ({'x': True}, {'x': True}),
    ({'ppa_dependencies': 'x,y,z'}, {'ppa_dependencies': ['x', 'y', 'z']}),
    ({'architectures': 'x,y,z'}, {'architectures': ['x', 'y', 'z']}),
    ({'releases': 'x,y,z'}, {'releases': ['x', 'y', 'z']}),
    ({'packages': 'x,y,z'}, {'packages': ['x', 'y', 'z']}),
    ])
def test_unpack_config(config, expected_config):
    '''Checks that processed config matches expectations.'''
    assert script.unpack_config(config) == expected_config


def test_create_lp_via_file(tmp_path):
    '''Checks loading of credentials provided by --credentials arg.'''
    expected_credentials = "[1]\na: 1\nb: 2\n"
    credentials_file = tmp_path / 'x'
    credentials_file.write_text(expected_credentials)

    lp = LpServiceMock()
    parser = script.create_arg_parser()
    args = parser.parse_args([
        '--credentials', str(credentials_file),
        'show', 'test-ppa',
    ])
    lp = script.create_lp('x', args)

    assert lp._credentials == expected_credentials


@patch.dict(os.environ, {"LP_CREDENTIALS": "[1]\na: 1\nb: 2\n"})
def test_create_lp_via_envvar(tmp_path):
    '''Checks loading of credentials provided by $LP_CREDENTIALS.'''
    lp = LpServiceMock()
    parser = script.create_arg_parser()
    args = parser.parse_args([
        'show', 'test-ppa',
    ])
    lp = script.create_lp('x', args)

    assert lp._credentials == os.environ['LP_CREDENTIALS']


@pytest.mark.parametrize('stdin, params, expected_ppa_config', [
    # Defaults
    (None, {}, {'description': ''}),

    # Overrides
    ('x', {}, {'description': 'x'}),
    (None, {'description': 'a'}, {'description': 'a'}),
    (None, {'ppa_name': 'a'}, {'displayname': 'a'}),
    (None, {'publish': True}, {'publish': True}),
    (None, {'publish': False}, {'publish': False}),
    (None, {'private': True}, {'private': True}),
    (None, {'private': False}, {'private': False}),
])
def test_command_create(fake_config, monkeypatch, stdin, params, expected_ppa_config):
    '''Checks create command produces a PPA with expected configuration.'''
    lp = LpServiceMock()
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))

    # Check success of the create command
    config = script.unpack_config({**fake_config, **params})
    print(config)
    assert script.command_create(lp, config) == 0

    # Retrieve the newly created PPA
    owner = lp.people[config['owner_name']]
    lp_ppa = owner.getPPAByName(config['ppa_name'])
    assert lp_ppa

    # Verify the expected items are present in the new PPA
    for key, value in expected_ppa_config.items():
        assert getattr(lp_ppa, key) == value


@pytest.mark.parametrize('params, owner_name', [
    # Defaults
    ({'owner_name': 'a', 'ppa_name': 'x'}, 'a'),
])
def test_command_create_with_owner(fake_config, monkeypatch, params, owner_name):
    '''Checks create command produces a PPA for a specified owner.'''
    lp = LpServiceMock()
    lp.launchpad.add_person(owner_name)
    monkeypatch.setattr("sys.stdin", io.StringIO('x'))

    # Check success of the create command
    config = script.unpack_config({**fake_config, **params})
    print(config)
    assert script.command_create(lp, config) == 0

    # Retrieve the newly created PPA
    owner = lp.people[owner_name]
    lp_ppa = owner.getPPAByName(config['ppa_name'])
    assert lp_ppa


@pytest.mark.parametrize('architectures, expected_processors', [
    (None, ARCHES_PPA_DEFAULT),
    ('a', ['a']),
    ('a,b,c', ['a', 'b', 'c']),
    ('a, b, c', ['a', 'b', 'c']),
    ('amd64,arm64,armhf,i386,powerpc,ppc64el,s390x',
     ["amd64", "arm64", "armhf", "i386", "powerpc", "ppc64el", "s390x"]),
])
def test_command_create_with_architectures(monkeypatch, fake_config, architectures, expected_processors):
    '''Checks that PPAs can be created with non-default architecture support.'''
    lp = LpServiceMock()
    config = script.unpack_config({**fake_config, **{'architectures': architectures}})
    monkeypatch.setattr("sys.stdin", io.StringIO('x'))
    assert script.command_create(lp, config) == 0

    # Retrieve the newly created PPA
    owner = lp.people[config['owner_name']]
    lp_ppa = owner.getPPAByName(config['ppa_name'])

    # Check processor architectures
    assert lp_ppa.processors
    assert type(lp_ppa.processors) is list
    assert [proc.name for proc in lp_ppa.processors] == expected_processors


@pytest.mark.parametrize('params, expected_filename', [
    ({}, 'credentials.oauth'),
    ({'credentials_filename': 'a'}, 'a'),
    ({'credentials_filename': '~/.x/creds.oauth'}, '~/.x/creds.oauth'),
])
def test_command_credentials(fake_config, params, expected_filename):
    """Check that credentials command saves LP creds to file."""
    lp = LpServiceMock()
    config = script.unpack_config({**fake_config, **params})

    assert script.command_credentials(lp, config) == 0
    lp.credentials.save_to_path.assert_called_once()


@pytest.mark.xfail(reason="Unimplemented")
def test_command_desc(fake_config):
    lp = LpServiceMock()
    assert script.command_desc(lp, fake_config) == 0
    # TODO: Assert that if --dry-run specified, there are no actual
    #   changes requested of launchpad
    # TODO: Verify the description gets set as expected


@pytest.mark.xfail(reason="Unimplemented")
def test_command_destroy(fake_config):
    lp = LpServiceMock()
    # TODO: Create a fake ppa to be destroyed
    assert script.command_destroy(lp, fake_config) == 0
    # TODO: Verify the ppa is requested to be deleted


@pytest.mark.xfail(reason="Unimplemented")
def test_command_list(fake_config):
    lp = LpServiceMock()
    # TODO: Create a fake ppa with contents to be listed
    assert script.command_list(lp, fake_config) == 0
    # TODO: Verify the ppa addresses get listed


@pytest.mark.xfail(reason="Unimplemented")
def test_command_exists(fake_config):
    lp = LpServiceMock()
    # TODO: Create fake ppa that exists
    assert script.command_exists(lp, fake_config) == 0
    # TODO: Verify this returns true when the ppa does exist


@pytest.mark.xfail(reason="Unimplemented")
def test_command_not_exists(fake_config):
    lp = LpServiceMock()
    # TODO: Verify this returns true when the ppa does not exist
    assert script.command_exists(lp, fake_config) == 1


@pytest.mark.parametrize('params, expected_ppa_config', [
    ({'displayname': 'a'}, {'displayname': 'a'}),
    ({'description': 'a'}, {'description': 'a'}),

    ({}, {'publish': True}),
    ({'publish': False}, {'publish': False}),
    ({'publish': True}, {'publish': True}),

    ({}, {'private': False}),
    ({'private': False}, {'private': False}),
    ({'private': True}, {'private': True}),
])
def test_command_set(fake_config, params, expected_ppa_config):
    '''Checks that the set command properly requests PPA configuration changes.'''
    lp = LpServiceMock()

    # Create a default PPA, for modification later
    owner = lp.people[fake_config['owner_name']]
    owner.createPPA(fake_config['ppa_name'], 'x', 'y')

    # Check success of the set command
    config = script.unpack_config({**fake_config, **params})
    assert script.command_set(lp, config)

    # Retrieve the PPA we created earlier
    lp_ppa = owner.getPPAByName(fake_config['ppa_name'])

    # Verify the expected items are present in the updated PPA
    for key, value in expected_ppa_config.items():
        assert getattr(lp_ppa, key) == value


@pytest.mark.parametrize('architectures, expected_processors', [
    (None, ARCHES_PPA_DEFAULT),
    ('a', ['a']),
    ('a,b,c', ['a', 'b', 'c']),
    ('a, b, c', ['a', 'b', 'c']),
    ('amd64,arm64,armhf,i386,powerpc,ppc64el,s390x',
     ["amd64", "arm64", "armhf", "i386", "powerpc", "ppc64el", "s390x"]),
])
def test_command_set_architectures(fake_config, architectures, expected_processors):
    '''Checks that existing PPAs can have their architectures changed.'''
    lp = LpServiceMock()

    # Create a default PPA, for modification later
    owner = lp.people[fake_config['owner_name']]
    owner.createPPA(fake_config['ppa_name'], 'x', 'y')

    # Check success of the set command
    config = script.unpack_config({**fake_config, **{'architectures': architectures}})
    assert script.command_set(lp, config)

    # Retrieve the PPA we created earlier
    lp_ppa = owner.getPPAByName(fake_config['ppa_name'])

    # Check processor architectures
    assert lp_ppa.processors
    assert type(lp_ppa.processors) is list
    assert [proc.name for proc in lp_ppa.processors] == expected_processors


@pytest.mark.parametrize('params, pubs, format, expected_in_stdout', [
    (
        # General behavior
        {
            'releases': None,
            'architectures': 'amd64',
            'show_urls': True
        },
        [('x', '1', 'Published', 'jammy')],
        'plain',
        'arch=amd64&trigger=x%2F1&ppa=me%2Ftesting'
    ),
    (
        # Specified release
        {
            'releases': 'focal',
            'architectures': 'amd64',
            'show_urls': True
        },
        [
            ('x', '3.2.1', 'Published', 'jammy'),
            ('x', '1.2.3', 'Published', 'focal'),
            ('x', '1.0.0', 'Published', 'bionic'),
        ],
        'plain',
        'arch=amd64&trigger=x%2F1.2.3&ppa=me%2Ftesting'
    ),
    (
        # Specified architectures can be comma-delimited strings
        {
            'releases': 'focal',
            'architectures': 'amd64,i386',
            'show_urls': True
        },
        [('x', '1.2.3', 'Published', 'focal')],
        'plain',
        'arch=i386&trigger=x%2F1.2.3&ppa=me%2Ftesting'
    ),
    (
        # Specified architectures can be provided as a list, too
        {
            'releases': 'focal',
            'architectures': ['amd64', 'i386', 's390x'],
            'show_urls': True
        },
        [('x', '1.2.3', 'Published', 'focal')],
        'plain',
        'arch=s390x&trigger=x%2F1.2.3&ppa=me%2Ftesting'
    ),
    (
        # Default behavior should include ESM releases (LP: #2038651)
        {
            'releases': None,
            'architectures': 'amd64',
            'show_urls': True
        },
        [
            ('x', '3.2.1', 'Published', 'jammy'),
            ('x', '1.2.3', 'Published', 'focal'),
            ('x', '1.0.0', 'Published', 'bionic'),
        ],
        'plain',
        'arch=amd64&trigger=x%2F1.0.0&ppa=me%2Ftesting'
    ),
])
@patch('urllib.request.urlopen')
@patch('ppa.io.open_url')
def test_command_show(urlopen_mock,
                      open_url_mock,
                      fake_config, capfd,
                      params, pubs, format, expected_in_stdout):
    '''Checks that the show command retrieves and displays correct results.'''
    lp = LpServiceMock()
    urlopen_mock.return_value = "{}"
    Ppa.get_autopkgtest_running = lambda x, y, z: []
    Ppa.get_autopkgtest_waiting = lambda x, y, z: []

    # Create a default PPA, for modification later
    owner = lp.people[fake_config['owner_name']]
    owner.createPPA(fake_config['ppa_name'], 'x', 'y')
    the_ppa = lp.me.getPPAByName(fake_config['ppa_name'])

    # Add some fake publications
    for pub in pubs:
        the_ppa.published_sources.append(PublicationMock(*pub))

    config = script.unpack_config({**fake_config, **params})
    assert script.command_show(lp, config) == 0
#    out, err = capfd.readouterr()
#    assert expected_in_stdout in out


@pytest.mark.parametrize('params, pubs, format, expected_in_stdout', [
    (
        # General behavior
        {
            'releases': None,
            'architectures': 'amd64',
            'show_urls': True
        },
        [('x', '1', 'Published', 'jammy')],
        'plain',
        'arch=amd64&trigger=x%2F1&ppa=me%2Ftesting'
    ),
    (
        # Specified release
        {
            'releases': 'focal',
            'architectures': 'amd64',
            'show_urls': True
        },
        [
            ('x', '3.2.1', 'Published', 'jammy'),
            ('x', '1.2.3', 'Published', 'focal'),
            ('x', '1.0.0', 'Published', 'bionic'),
        ],
        'plain',
        'arch=amd64&trigger=x%2F1.2.3&ppa=me%2Ftesting'
    ),
    (
        # Specified architectures can be comma-delimited strings
        {
            'releases': 'focal',
            'architectures': 'amd64,i386',
            'show_urls': True
        },
        [('x', '1.2.3', 'Published', 'focal')],
        'plain',
        'arch=i386&trigger=x%2F1.2.3&ppa=me%2Ftesting'
    ),
    (
        # Specified architectures can be provided as a list, too
        {
            'releases': 'focal',
            'architectures': ['amd64', 'i386', 's390x'],
            'show_urls': True
        },
        [('x', '1.2.3', 'Published', 'focal')],
        'plain',
        'arch=s390x&trigger=x%2F1.2.3&ppa=me%2Ftesting'
    ),
    (
        # Default behavior should include ESM releases (LP: #2038651)
        {
            'releases': None,
            'architectures': 'amd64',
            'show_urls': True
        },
        [
            ('x', '3.2.1', 'Published', 'jammy'),
            ('x', '1.2.3', 'Published', 'focal'),
            ('x', '1.0.0', 'Published', 'bionic'),
        ],
        'plain',
        'arch=amd64&trigger=x%2F1.0.0&ppa=me%2Ftesting'
    ),
])
@patch('urllib.request.urlopen')
@patch('ppa.io.open_url')
def test_command_tests(urlopen_mock,
                       open_url_mock,
                       fake_config, capfd,
                       params, pubs, format, expected_in_stdout):
    '''Checks that the tests command retrieves and displays correct results.'''
    lp = LpServiceMock()
    urlopen_mock.return_value = "{}"
    Ppa.get_autopkgtest_running = lambda x, y, z: []
    Ppa.get_autopkgtest_waiting = lambda x, y, z: []

    # Create a default PPA, for modification later
    owner = lp.people[fake_config['owner_name']]
    owner.createPPA(fake_config['ppa_name'], 'x', 'y')
    the_ppa = lp.me.getPPAByName(fake_config['ppa_name'])

    # Add some fake publications
    for pub in pubs:
        the_ppa.published_sources.append(PublicationMock(*pub))

    config = script.unpack_config({**fake_config, **params})
    assert script.command_tests(lp, config) == 0
    out, err = capfd.readouterr()
    assert expected_in_stdout in out


@pytest.mark.xfail(reason="Unimplemented")
def test_command_wait(fake_config):
    lp = LpServiceMock()
    # TODO: Set wait period to 1 sec
    assert script.command_wait(lp, fake_config) == 0
