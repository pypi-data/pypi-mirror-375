#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2022 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Tests Results class as representing an Autopkgtest test log and status."""

import os
import sys
import time

import gzip
import json
import pytest
from typing import List, Dict

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))
DATA_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "data"))

from ppa.result import Result, get_results, show_results
from ppa.subtest import Subtest
from ppa.io import open_url


def test_object():
    """Checks that Result objects can be instantiated."""
    timestamp = time.strptime('20030201_040506', "%Y%m%d_%H%M%S")
    result = Result('url', timestamp, 'ser', 'arch', 'src')
    assert result
    assert result.url == 'url'
    assert result.time == timestamp
    assert result.series == 'ser'
    assert result.arch == 'arch'
    assert result.source == 'src'
    assert not result.error_message


@pytest.mark.parametrize('pub_dict, expected_repr', [
    (
        {'url': 'url', 'time': None, 'series': 'ser', 'arch': 'arch', 'source': 'src'},
        "Result(url='url', time=None, series='ser', arch='arch', source='src')",
    )
])
def test_repr(pub_dict, expected_repr):
    """Checks Result object representation."""
    result = Result(**pub_dict)
    assert repr(result) == expected_repr


@pytest.mark.parametrize('pub_dict, expected_str', [
    (
        {
            'url': 'url',
            'time': time.strptime('20030201_040506', "%Y%m%d_%H%M%S"),
            'series': 'ser',
            'arch': 'arch',
            'source': 'src',
        },
        'src on ser for arch    @ 01.02.03 04:05:06',
    )
])
def test_str(pub_dict, expected_str):
    """Checks Result object textual presentation."""
    result = Result(**pub_dict)
    assert f"{result}" == expected_str


@pytest.mark.parametrize('timestamp, subtests, show_urls, expected', [
    (
        # With show_urls enabled, output should show a text URL.
        '20030201_040506',
        [],
        True,
        """    + ✅ source on series for arch    @ 01.02.03 04:05:06
      • Log: file://<DATA_DIR>/x
"""
    ),
    (
        # Without show_urls, output should create console-clickable URLs.
        '20030201_040506',
        [],
        False,
        """    + ✅ source on series for arch    @ 01.02.03 04:05:06  \x1b]8;;file://<DATA_DIR>/x\x1b\\Log️ 🗒️ \x1b]8;;\x1b\\
"""
    ),
    (
        # When no Subtests fail, no detailed results should be shown.
        '20030201_040506',
        [Subtest('x PASS'), Subtest('y PASS'), Subtest('z SKIP')],
        True,
        """    + ✅ source on series for arch    @ 01.02.03 04:05:06
      • Log: file://<DATA_DIR>/x
"""
    ),
    (
        # When at least one Subtest fails, all subtest results should be shown.
        '20030201_040506',
        [Subtest('x PASS'), Subtest('y FAIL'), Subtest('f FLAKY'), Subtest('z SKIP')],
        True,
        """    + ❌ source on series for arch    @ 01.02.03 04:05:06
      • Log: file://<DATA_DIR>/x
      • Status: FAIL
      • x                         PASS   🟩
      • y                         FAIL   🟥
      • f                         FLAKY  🟫
      • z                         SKIP   🟧
"""
    ),
])
def test_to_bullet_tree(timestamp, subtests, show_urls, expected):
    """Checks representation of Result as a bullet-tree text list."""
    tm = time.strptime(timestamp, "%Y%m%d_%H%M%S")
    result = Result(f"file://{DATA_DIR}/x", tm, 'series', 'arch', 'source')

    # Substitute in our fake subtest data in place of Result's get_subtests() routine
    result.get_subtests = lambda: subtests

    out = result.to_bullet_tree(show_urls)
    assert out == expected.replace("<DATA_DIR>", DATA_DIR)


def test_timestamp():
    """Checks Result object formats the result's time correctly."""
    timestamp = time.strptime('20030201_040506', "%Y%m%d_%H%M%S")
    result = Result('url', timestamp, 'b', 'c', 'd')
    assert f"{result.timestamp}" == '01.02.03 04:05:06'


def test_log(tmp_path):
    """Checks that the log content of a Result is available."""
    f = tmp_path / "result.log.gz"
    compressed_text = gzip.compress(bytes('abcde', 'utf-8'))
    f.write_bytes(compressed_text)

    result = Result(f"file://{f}", None, None, None, None)
    assert result.log == "abcde"


@pytest.mark.parametrize('filename, expected_triggers', [
    ('results-rabbitmq-server-armhf.log.gz', ['rabbitmq-server/3.9.27-0ubuntu0.1~jammy8']),
    ('results-six-s390x.log.gz', ['pygobject/3.42.2-2', 'six/1.16.0-4']),
    ('results-chrony-armhf.log.gz', ['dpkg/1.22.6ubuntu5'])
])
def test_triggers(filename, expected_triggers):
    """Checks that autopkgtest triggers can be extracted from test result logs."""
    result = Result(f"file://{DATA_DIR}/{filename}", None, None, None, None)
    assert result.triggers == expected_triggers


@pytest.mark.parametrize('triggers, name, arch, series, expected', [
    ([], None, 'arch', 'ser', []),
    (
        # Single trigger
        ['pkg/1'],
        'pkg', 'arch', 'ser',
        [
            (
                "Trigger(source_publication=SourcePublication(package='pkg', "
                "version='1', series='ser', archive=None, status=None), "
                "architecture='arch', test_package='pkg')"
            )
        ],
    ),
    pytest.param(
        # Multiple triggers
        ['pkg/1', 'x/2', 'y/3', 'z/4'],
        'pkg', 'arch', 'ser',
        [
            (
                "Trigger(source_publication=SourcePublication(package='pkg', "
                "'version='1', series='ser', archive=None, status=None), "
                "architecture='arch', test_package='pkg')"
            ),
            (
                "Trigger(source_publication=SourcePublication(package='x', "
                "'version='2', series='ser', archive=None, status=None), "
                "architecture='arch', test_package='pkg')"
            ),
            (
                "Trigger(source_publication=SourcePublication(package='y', "
                "'version='3', series='ser', archive=None, status=None), "
                "architecture='arch', test_package='pkg')"
            ),
            (
                "Trigger(source_publication=SourcePublication(package='z', "
                "'version='4', series='ser', archive=None, status=None), "
                "architecture='arch', test_package='pkg')"
            ),
        ],
        marks=pytest.mark.xfail(reason="Trigger and test packages reversed?"),
    ),
])
def test_get_triggers(monkeypatch, triggers, name, arch, series, expected):
    """Checks retrieval of Trigger objects from autopkgtest results."""
    result = Result('url', time=None, arch=arch, series=series, source=None)
    monkeypatch.setattr(Result, "triggers", triggers)

    triggers = result.get_triggers(name)
    assert [repr(t) for t in triggers] == expected


@pytest.mark.parametrize('log_text, subtest_name, expected', [
    ('', None, {'testbed': 'BAD'}),
    (
        (
            "x: @@@@@@@@@@@@@@@@@@@@ summary\n"
            "test-a          PASS\n"
            "test-b          FAIL ignorable-note\n"
            "test-c          FLAKY some-detail\n"
            "test-d          NoTaVaLiDsTaTuS\n"
        ),
        None,
        {'test-a': 'PASS', 'test-b': 'FAIL', 'test-c': 'FLAKY'}
    ),
    (
        (
            "autopkgtest [21:13:56]: starting date: 2022-11-18\n"
            "The following packages have unmet dependencies:\n"
            " builddeps:.../12-autopkgtest-satdep.dsc:i386 : Depends: gcc:i386 but it is not installable\n"
            "E: Unable to correct problems, you have held broken packages.\n"
            "chroot               FAIL badpkg\n"
            "blame: apache2\n"
            "badpkg: Test dependencies are unsatisfiable. A common reason is ...\n"
            "autopkgtest [21:48:03]: @@@@@@@@@@@@@@@@@@@@ summary\n"
            "run-test-suite       FAIL badpkg\n"
            "blame: apache2\n"
            "badpkg: Test dependencies are unsatisfiable. A common reason is...\n"
            "duplicate-module-load PASS\n"
            "default-mods         PASS\n"
            "run-htcacheclean     PASS\n"
            "ssl-passphrase       PASS\n"
            "check-http2          PASS\n"
            "run-chroot           FAIL badpkg\n"
            "blame: apache2\n"
        ),
        'run-',
        {
            'run-test-suite': 'FAIL',
            'run-htcacheclean': 'PASS',
            'run-chroot': 'FAIL',
        }
    ),
    (
        (
            "3657s rm: cannot remove '.../mountpoint': Device or resource busy\n"
            "3661s autopkgtest [03:41:43]: test minimized: -----------------------]\n"
            "3663s autopkgtest [03:41:45]: test minimized:  - - - - - - - - - - results - - - - - - - - - -\n"
            "3663s minimized            FAIL non-zero exit status 1\n"
            "3663s autopkgtest [03:41:45]: test minimized:  - - - - - - - - - - stderr - - - - - - - - - -\n"
            "3663s rm: cannot remove '.../mountpoint': Device or resource busy\n"
            "3664s autopkgtest [03:41:46]: @@@@@@@@@@@@@@@@@@@@ summary\n"
            "3664s default-bootstraps   FAIL non-zero exit status 1\n"
            "3664s minimized            FAIL non-zero exit status 1'\n"
        ),
        None,
        {
            'default-bootstraps': 'FAIL',
            'minimized': 'FAIL'
        }
    ),
])
def test_get_subtests(tmp_path, log_text: str, subtest_name: str, expected: Dict[str, str]):
    """Checks retrieval of Subtest objects from autopkgtest results.

    This test exercises the parser that extracts subtest information out
    of autopkgtest logs of various formats.  It also verifies the
    parameter to get_subtests() is handled correctly.

    :param fixture tmp_path: Temp dir.
    :param str log_text: Text to write into the log file.
    :param str subtest_name: Only retrieve subtests starting with this text.
    :param Dict[str] expected: Dictionary of subtest names to pass/fail status.
    """
    f = tmp_path / "result.log.gz"
    compressed_text = gzip.compress(bytes(log_text, 'utf-8'))
    f.write_bytes(compressed_text)

    result = Result(f"file://{f}", None, None, None, None)
    subtests = result.get_subtests(subtest_name)
    assert {s.desc: s.status for s in subtests} == expected


@pytest.mark.parametrize('subtest_states, error_message, expected', [
    ([], None, 'PASS'),
    (['PASS'], None, 'PASS'),
    (['FAIL'], None, 'FAIL'),
    (['SKIP'], None, 'PASS'),
    (['FLAKY'], None, 'PASS'),
    (['PASS', 'FAIL'], None, 'FAIL'),
    (['FAIL', 'PASS'], None, 'FAIL'),
    (['PASS', 'PASS', 'PASS'], None, 'PASS'),
    (['PASS', 'FLAKY'], None, 'PASS'),
    (['PASS', 'SKIP'], None, 'PASS'),
    (['PASS'], 'x', 'BAD'),
    (['FAIL'], 'x', 'BAD'),
])
def test_status(monkeypatch, subtest_states, error_message, expected):
    """Checks retrieval of status from autopkgtest results."""
    result = Result("file://tmp/x", None, None, None, None)
    result.error_message = error_message

    # Add subtests with given states
    subtests = [Subtest(f"... {state}...") for state in subtest_states]
    monkeypatch.setattr(Result, "get_subtests", lambda x: subtests)

    assert result.status == expected


@pytest.mark.parametrize('status, expected', [
    ('PASS', "✅"),
    ('FAIL', "❌"),
    ('BAD', "⛔"),
])
def test_status_icon(monkeypatch, status, expected):
    """Checks generation of correct icon based on autopkgtest results."""
    result = Result("file://tmp/x", None, None, None, None)
    monkeypatch.setattr(Result, "status", status)

    assert result.status_icon == expected


@pytest.mark.parametrize('status, expected_exception', [
    (None, KeyError),
    ('x', KeyError),
])
def test_status_icon_error(monkeypatch, status, expected_exception):
    """Checks generation of correct icon based on autopkgtest results."""
    result = Result("file://tmp/x", None, None, None, None)
    monkeypatch.setattr(Result, "status", status)

    with pytest.raises(expected_exception):
        print(result.status_icon)


@pytest.mark.parametrize('log_text, series, arch, source, expected_dict', [
    (
        # Empty/invalid log should return empty triggers
        'x', 'x', 'x', 'x', {'triggers': []}
    ),

    (
        # Empty/invalid log counts as an overall test state BAD.
        'x', 'x', 'x', 'x',
        {
            'status': 'BAD',
            'status_icon': '⛔',
            'subtests': [
                {
                    'desc': 'testbed',
                    'line': 'testbed setup failure  BAD',
                    'status': 'BAD',
                    'status_icon': '⛔'
                }
            ]
        }
    ),

    (
        # Init parameters are registered in the class as provided.
        'l', 's', 'a', 'pkg', {'log': 'l', 'series': 's', 'arch': 'a', 'source': 'pkg'}
    ),

    (
        # Log with valid syntax for a trigger should create a Trigger dict.
        '--env=ADT_TEST_TRIGGERS=t/1 -- \n: @@@@@@@@@@@@@@@@@@@@', 's', 'a', 'pkg',
        {
            'triggers': [
                {
                    'source_publication': {
                        'archive': None,
                        'package': 't',
                        'version': '1',
                        'status': None,
                        'series': 's',
                    },
                    'architecture': 'a',
                    'test_package': 't',
                },
            ]
        }
    ),

    (
        # Log with valid syntax for a subtest should create a Subtest dict.
        ': @@@@@@@@@@@@@@@@@@@@ summary\n999s tst FAIL', 's', 'a', 'pkg',
        {
            'subtests': [
                {
                    'desc': 'tst',
                    'line': 'tst FAIL',
                    'status': 'FAIL',
                    'status_icon': '🟥'
                },
            ],
            'status': 'FAIL',
            'status_icon': '❌'
        }
    )
])
def test_to_dict(tmp_path, log_text, series, arch, source, expected_dict):
    """Checks Result object structural representation."""
    f = tmp_path / "result.log.gz"
    f.write_bytes(gzip.compress(bytes(log_text, 'utf-8')))
    timestamp = time.strptime('20030201_040506', "%Y%m%d_%H%M%S")
    result = Result(f"file://{f}", timestamp, series, arch, source)
    expected_keys = [
        'url', 'timestamp', 'series', 'arch', 'source',
        'error_message', 'log', 'triggers', 'subtests', 'status',
        'status_icon'
    ]
    expected_types = [str, type(None), list]

    d = result.to_dict()
    assert isinstance(d, dict), f"type of d is {type(d)} not dict"

    # Verify expected keys are present
    assert sorted(d.keys()) == sorted(expected_keys)

    # Verify values are within set of expected types
    for k, v in d.items():
        assert type(v) in expected_types, f"'{k}={v}' is unexpected type {type(v)}"

    # Verify values match what we expect
    for k, v in expected_dict.items():
        assert v == d.get(k)

    # Verify full dict can be written as JSON
    try:
        assert json.dumps(d)
    except UnicodeDecodeError as e:
        assert False, f"Wrong UTF codec detected: {e}"
    except json.JSONDecodeError as e:
        assert False, f"JSON decoding error: {e.msg}, {e.doc}, {e.pos}"


@pytest.mark.parametrize('results_text, arches, sources, expected', [
    (
        # Specifying no args should return all logs
        "noble/amd64/e/exim4/20240104_193939_e912d@/log.gz\n",
        None,
        None,
        ["/results/noble/amd64/e/exim4/20240104_193939_e912d@/log.gz'"],
    ),
    (
        # Specifying empty args should return all logs
        "noble/amd64/e/exim4/20240104_193939_e912d@/log.gz\n",
        [],
        [],
        ["/results/noble/amd64/e/exim4/20240104_193939_e912d@/log.gz'"],
    ),
    (
        # Specifying a missing architecture should return no results
        "noble/amd64/e/exim4/20240104_193939_e912d@/log.gz",
        ['a'],
        None,
        []
    ),
    (
        # Specifying an unrelated package should return no results
        "noble/amd64/e/exim4/20240104_193939_e912d@/log.gz\n",
        None,
        ['pkg'],
        []
    ),
    (
        # Specifying an arch and package present should return
        # corresponding result
        'noble/amd64/e/exim4/20240104_193939_e912d@/log.gz',
        ['amd64'],
        ['exim4'],
        ["/results/noble/amd64/e/exim4/20240104_193939_e912d@/log.gz'"],
    ),
    (
        # Specified architectures should provide results for those
        # architectures and no others.
        (
            "noble/amd64/e/exim4/20240104_193939_e912d@/log.gz\n"
            "noble/armhf/e/exim4/20240104_193939_e912d@/log.gz\n"
            "noble/arm64/e/exim4/20240104_193939_e912d@/log.gz\n"
            "noble/i386/e/exim4/20240104_193939_e912d@/log.gz\n"
        ),
        ['amd64', 'armhf', 'i386'],
        ['exim4'],
        [
            "/results/noble/amd64/e/exim4/20240104_193939_e912d@/log.gz'",
            "/results/noble/armhf/e/exim4/20240104_193939_e912d@/log.gz'",
            "/results/noble/i386/e/exim4/20240104_193939_e912d@/log.gz'",
        ],
    ),
    (
        # Specifying mix of present and missing architectures should
        # correctly return proper subset of matches.
        (
            "noble/amd64/e/exim4/20240104_193939_e912d@/log.gz\n"
            "noble/armhf/e/exim4/20240104_193939_e912d@/log.gz\n"
            "noble/arm64/e/exim4/20240104_193939_e912d@/log.gz\n"
            "noble/i386/e/exim4/20240104_193939_e912d@/log.gz\n"
        ),
        ['amd64', 'x', 'y', 'z'],
        ['exim4'],
        [
            "/results/noble/amd64/e/exim4/20240104_193939_e912d@/log.gz'",
        ],
    ),
    (
        # Specifying a mix of present and missing packages should
        # correctly return proper subset of matches.
        (
            "noble/amd64/x/xxx/20240104_193939_e912d@/log.gz\n"
            "noble/amd64/y/yyy/20240104_193939_e912d@/log.gz\n"
        ),
        ['amd64'],
        ['xxx', 'yyy', 'zzz', 'non-existing'],
        [
            "/results/noble/amd64/x/xxx/20240104_193939_e912d@/log.gz'",
            "/results/noble/amd64/y/yyy/20240104_193939_e912d@/log.gz'",
        ],
    ),
])
def test_get_results(tmp_path,
                     results_text: str,
                     arches: 'List[str]|None',
                     sources: 'List[str]|None',
                     expected: List[str]):
    """Checks that expected results can be found from autopkgtest logs."""
    f = tmp_path / "results"
    f.write_text(results_text)
    url = f"file://{f}"
    response = open_url(url)
    assert response

    results = list(get_results(response, url, arches, sources))
    print("results: ", results)

    # Verify expected number, type, and representation of returned results
    assert len(results) == len(expected)
    assert all([isinstance(result, Result) for result in results])
    for r in results:
        # Verify the repr starts with the expected class name
        assert repr(r).startswith("Result(url='")

        # Verify that at least one of the expected strings is present
        # somewhere in the repr output string.
        assert True in [e in repr(r) for e in expected], \
            f"None of {expected} found in {repr(r)}"


@pytest.mark.parametrize('data, show_urls, expected_num_lines, expected_in_stdout', [
    (
        # When there are no results, indicate '(none)'
        {}, True, 1, "* Results: (none)\n"
    ),
    (
        {'trigger-1': ('a', 'b', 'c', 'x')}, True, 6, "- trigger-1\n    + ⛔ c on a for b"
    ),
    ({'t1': ('a', 'b', 'c', 'x'), 't2': ('a', 'b', 'c', 'x')}, True, 11, "- t2"),
])
def test_show_results(capfd, tmp_path,
                      data, show_urls, expected_num_lines, expected_in_stdout):
    """Checks that results output includes the expected text."""
    results = []
    for trigger, (series, arch, source, item) in data.items():
        trigger_sets = {}
        trigger_sets.setdefault(trigger, [])
        f = tmp_path / f"{trigger}-result.log.gz"
        compressed_text = gzip.compress(bytes(item, 'utf-8'))
        f.write_bytes(compressed_text)
        timestamp = time.strptime('20030201_040506', "%Y%m%d_%H%M%S")
        result = Result(f"file://{f}", timestamp, series, arch, source)
        trigger_sets[trigger].append(result)
        results.append(trigger_sets)

    show_results(results, show_urls)

    out, err = capfd.readouterr()
    print(out)
    assert out.count('\n') == expected_num_lines
    assert expected_in_stdout in out
