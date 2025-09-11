#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Copyright (C) 2022 Authors
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.
#
# Authors:
#   Bryce Harrington <bryce@canonical.com>

"""Top-level code for analyzing an Ubuntu Apt repository."""

import os.path
from functools import lru_cache
from typing import Dict

from .suite import Suite
from .constants import (
    LOCAL_REPOSITORY_PATH,
    LOCAL_REPOSITORY_MIRRORING_DIRECTIONS
)


class Repository:
    """Top-level class for analyzing an Ubuntu Apt repository.

    This class and its children serves as a wrapper to a local mirror of
    a Ubuntu Apt repository.  Repository provides an entry interface to
    the Apt data, allowing lazy lookup of the package data in various ways.
    """

    def __init__(self, cache_dir: str):
        """Initialize a new Repository object for an Apt cache.

        :param str cache_dir: The path to the top level of the local Apt mirror.
        """
        if not cache_dir:
            raise ValueError("undefined cache_dir.")
        if not os.path.isdir(cache_dir):
            raise FileNotFoundError(f"could not find cache dir '{cache_dir}'")

        self.cache_dir = cache_dir

    def __repr__(self):
        """Return a machine-parsable unique representation of object.

        :rtype: str
        :returns: Official string representation of the object.
        """
        return (f'{self.__class__.__name__}('
                f'cache_dir={self.cache_dir!r})')

    @property
    @lru_cache
    def suites(self) -> Dict[str, Suite]:
        """The release pockets available in this repository.

        :returns: Mapping of Ubuntu release pockets to corresponding Suite objects.
        :rtype: Dict[str, Suite]
        """
        return {
            suite_name: Suite(suite_name, os.path.join(self.cache_dir, suite_name))
            for suite_name
            in os.listdir(self.cache_dir)
            if os.path.isdir(os.path.join(self.cache_dir, suite_name))
        }

    def get_suite(self, series_codename: str, pocket: str) -> Suite:
        """Retrieve a Suite object by its codename and pocket.

        The pocket name 'release' is treated as synonymous with '',
        since Apt stores the release suite without the pocket name.  In
        other words, 'lunar-release' is the same as 'lunar'.

        :param str series_codename: The Ubuntu release textual name.
        :param str pocket: The name of the pocket ('proposed', etc.)
        :returns: Corresponding Suite object.
        :rtype: Suite
        """
        if pocket == "release":
            release_pocket = series_codename
        else:
            release_pocket = f"{series_codename}-{pocket}"
        return self.suites.get(release_pocket, None)


if __name__ == "__main__":
    import sys
    from pprint import PrettyPrinter
    pp = PrettyPrinter(indent=4)

    from .debug import error

    print('#########################')
    print('## PpaGroup smoke test ##')
    print('#########################')

    local_dists_path = os.path.join(LOCAL_REPOSITORY_PATH, "dists")
    if not os.path.exists(local_dists_path):
        error(f'Missing checkout for smoketest\n{LOCAL_REPOSITORY_MIRRORING_DIRECTIONS}')
        sys.exit(1)
    repository = Repository(cache_dir=local_dists_path)
    for suite in repository.suites.values():
        print(suite)
        print(f'  series:      {suite.series_codename}')
        print(f'  components:  {", ".join(suite.components)}')
