#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Copyright (C) 2022 Authors
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.
#
# Authors:
#   Bryce Harrington <bryce@canonical.com>

"""An individual DEP8 test run."""

import json
from functools import lru_cache


class Subtest:
    """An autopkgtest sub-component test run.

    A triggered autopkgtest can invoke multiple DEP8 tests, such as running
    checks on dependencies, the software's testsuite, and integration tests.
    Each of these is considered a "Subtest"
    """
    VALUES = {
        'PASS': "🟩",
        'SKIP': "🟧",
        'FAIL': "🟥",
        'FLAKY': "🟫",
        'BAD': "⛔",
        'UNKNOWN': "⚪"
    }

    def __init__(self, line):
        """Initialize a new Subtext object.

        :param str line: The subtest result summary from a test log.
        """
        if not line:
            raise ValueError("undefined line.")

        self._line = line

    def __repr__(self) -> str:
        """Return a machine-parsable unique representation of object.

        :rtype: str
        :returns: Official string representation of the object.
        """
        return (f'{self.__class__.__name__}('
                f'line={self._line!r})')

    def __str__(self) -> str:
        """Return a human-readable summary of the object.

        :rtype: str
        :returns: Printable summary of the object.
        """
        return f"{self.desc:25} {self.status:6} {self.status_icon}"

    @lru_cache
    def to_dict(self) -> dict:
        """Return a basic dict structure of the Subtest's data."""
        return {
            'line': self._line,
            'desc': self.desc,
            'status': self.status,
            'status_icon': self.status_icon
        }

    @property
    @lru_cache
    def desc(self) -> str:
        """The descriptive text for the given subtest.

        :rtype: str
        :returns: Descriptive text.
        """
        return next(iter(self._line.split()), '')

    @property
    @lru_cache
    def status(self) -> str:
        """The success or failure of the given subtest.

        :rtype: str
        :returns: Status term in capitalized letters (PASS, FAIL, etc.)
        """
        for k in Subtest.VALUES:
            if f" {k}" in self._line:
                return k
        return 'UNKNOWN'

    @property
    @lru_cache
    def status_icon(self) -> str:
        """A unicode symbol corresponding to subtest's status.

        :rtype: str
        :returns: Single unicode character matching the status.
        """
        return Subtest.VALUES[self.status]


if __name__ == "__main__":
    print('##############################')
    print('## Subtest class smoke test ##')
    print('##############################')
    print()

    print("Valid cases")
    print("-----------")
    print(Subtest('subtest-a   UNKNOWN'))
    print(Subtest('subtest-b   PASS'))
    print(Subtest('subtest-c   FAIL'))
    print(Subtest('subtest-d   FAIL non-zero exit status 123'))
    print(Subtest('subtest-e   SKIP'))
    print(Subtest('subtest-f   BAD'))
    print(Subtest('librust-clang-sys-dev:clang_10_0 FAIL non-zero exit status 101'))
    print(Subtest('librust-clang-sys-dev:static FLAKY non-zero exit status 101'))
    print()

    print("Invalid cases")
    print("-------------")
    print(Subtest('invalid subtest: invalid'))
    print(Subtest('bAd subtest: bAd'))
    print()

    print("Object Dump")
    print("-----------")
    s = Subtest('librust-clang-sys-dev:clang_10_0 FAIL non-zero exit status 101')
    print(json.dumps(s.to_dict(), indent=4))
    print()
