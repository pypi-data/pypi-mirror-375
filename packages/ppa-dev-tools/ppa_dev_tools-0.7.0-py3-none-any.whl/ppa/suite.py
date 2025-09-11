#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Copyright (C) 2022 Authors
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.
#
# Authors:
#   Bryce Harrington <bryce@canonical.com>

"""Interprets and analyzes an Ubuntu Apt suite (aka release-pocket)."""

import os.path
from functools import lru_cache
from typing import Dict, List

# pylint: disable = no-name-in-module
import apt_pkg

from .source_package import SourcePackage
from .binary_package import BinaryPackage
from .constants import (
    DISTRO_UBUNTU_COMPONENTS,
    DISTRO_UBUNTU_POCKETS,
    LOCAL_REPOSITORY_PATH,
    LOCAL_REPOSITORY_MIRRORING_DIRECTIONS
)


class Suite:
    """A pocket of a Ubuntu series collecting source and binary package releases.

    Suites are named "<series>-<pocket>", such as "focal-updates" or
    "jammy-proposed".  The same package can have different versions in
    each Suite, but within a Suite each package will have no more than
    one version available at a time.
    """
    def __init__(self, suite_name: str, cache_dir: str):
        """Initialize a new Suite object for a given release pocket.

        :param str series_codename: The textual name of the Ubuntu release.
        :param str pocket: The pocket name ('release', 'proposed', 'backports', etc.)
        :param str cache_dir: The path to the given suite in the local Apt mirror.
        """
        if not suite_name:
            raise ValueError('undefined suite_name.')
        if not cache_dir:
            raise ValueError('undefined cache_dir.')
        if not os.path.exists(cache_dir):
            raise FileNotFoundError(f"could not find cache dir '{cache_dir}'")

        self._suite_name = suite_name
        self._cache_dir = cache_dir
        self._provides_table = None
        self._rdepends_table = None

    def __repr__(self) -> str:
        """Return a machine-parsable unique representation of object.

        :rtype: str
        :returns: Official string representation of the object.
        """
        return (
            f'{self.__class__.__name__}('
            f'suite_name={self._suite_name!r}, '
            f'cache_dir={self._cache_dir!r})'
        )

    def __str__(self) -> str:
        """Return a human-readable textual description of the Suite.

        :rtype: str
        :returns: Human-readable string.
        """
        return f'{self._suite_name}'

    def _rebuild_lookup_tables(self) -> bool:
        """Regenerate the provides and rdepends lookup tables.

        Some packages have build dependence that can be satisfied by one
        of several packages.  For example, a package may require either
        awk or mawk to build.  In these cases, the package will be
        registered in the table as an rdepend for BOTH awk and mawk.

        :rtype: bool
        :returns: True if tables were rebuilt, False otherwise"""
        self._provides_table = {}
        self._rdepends_table = {}
        for source_name, source in self.sources.items():
            for build_dep_binary_names in source.build_dependencies.keys():
                # This needs to deal with two different kinds of keys.
                # Basic dependencies are just simple str's, while alternate
                # dependencies are modeled as tuples.
                #
                # So, convert simple str's into single-element lists, so
                # both cases can be handled via iteration in a for loop.
                if isinstance(build_dep_binary_names, str):
                    build_dep_binary_names = [build_dep_binary_names]
                for build_dep_binary_name in build_dep_binary_names:
                    self._rdepends_table.setdefault(build_dep_binary_name, [])
                    self._rdepends_table[build_dep_binary_name].append(source)

            for provided_binary_name in source.provides_binaries.keys():
                self._provides_table[provided_binary_name] = source
        return self._provides_table and self._rdepends_table

    @property
    @lru_cache
    def info(self) -> Dict[str, str]:
        """The parsed Apt Release file for the suite as a dict.

        :rtype: dict[str, str]
        """
        info = None
        with apt_pkg.TagFile(f'{self._cache_dir}/Release') as tagfile:
            info = next(tagfile)
        if not info:
            raise ValueError(f'Could not load {self._cache_dir}/Release')
        return info

    @property
    def name(self) -> str:
        """The name of the suite as recorded in the apt database.

        :rtype: str
        """
        suite_name = self.info.get('Suite')
        if not suite_name:
            raise ValueError('Could not get suite name from info dict.')
        return suite_name

    @property
    def series_codename(self) -> str:
        """The textual name of the Ubuntu release for this suite.

        :rtype: str
        """
        return self.name.split('-')[0]

    @property
    def pocket(self) -> str:
        """The category of the archive (release, proposed, security, et al).

        :rtype: str
        """
        if '-' not in self.name:
            return 'release'
        pocket = self.name.split('-')[1]
        if pocket not in DISTRO_UBUNTU_POCKETS:
            raise RuntimeError(f'Unrecognized pocket "{pocket}"')
        return pocket

    @property
    def architectures(self) -> List[str]:
        """The list of CPU hardware types supported by this suite.

        :rtype: list[str]
        """
        architectures = self.info.get('Architectures').split()
        if not architectures:
            raise RuntimeError('Could not load architectures from info')
        return architectures

    @property
    def components(self) -> List[str]:
        """The sections of the archive provided in this suite.

        Components may include main, universe, etc.

        :rtype: list[str]
        """
        components = [
            component
            for component in os.listdir(self._cache_dir)
            if os.path.isdir(os.path.join(self._cache_dir, component))
            and component in DISTRO_UBUNTU_COMPONENTS
        ]
        if not components:
            raise RuntimeError(f'Could not load components from {self._cache_dir}')
        return components

    @property
    @lru_cache
    def sources(self) -> Dict[str, SourcePackage]:
        """The collection of source packages included in this suite.

        All source packages in all components are returned as
        SourcePackage objects.

        :rtype: dict[str, SourcePackage]
        """
        sources = None
        for sources_file in ['Sources.xz', 'Sources.gz']:
            for comp in self.components:
                source_packages_dir = f'{self._cache_dir}/{comp}/source'
                try:
                    with apt_pkg.TagFile(f'{source_packages_dir}/{sources_file}') as pkgs:
                        if sources is None:
                            sources = {}
                        for pkg in pkgs:
                            name = pkg['Package']
                            sources[name] = SourcePackage(dict(pkg))
                except apt_pkg.Error:
                    pass
            if sources is not None:
                return sources
        raise RuntimeError(f'Could not load {source_packages_dir}/Sources.[xz|gz]')

    @property
    @lru_cache
    def binaries(self) -> Dict[str, BinaryPackage]:
        """The collection of binary Deb packages included in this suite.

        All binary packages in all components are returned as
        BinaryPackage objects.

        :rtype: dict[str, BinaryPackage]
        """
        binaries = None
        for packages_file in ["Packages.xz", "Packages.gz"]:
            for comp in self.components:
                for arch in self.architectures:
                    binary_packages_dir = f'{self._cache_dir}/{comp}/binary-{arch}'
                    try:
                        with apt_pkg.TagFile(f'{binary_packages_dir}/{packages_file}') as pkgs:
                            if binaries is None:
                                binaries = {}
                            for pkg in pkgs:
                                name = f'{pkg["Package"]}:{arch}'
                                binaries[name] = BinaryPackage(pkg)
                    except apt_pkg.Error:
                        pass
            if binaries is not None:
                return binaries
        raise ValueError(f'Could not load {binary_packages_dir}/Packages.[xz|gz]')

    def dependent_packages(self, source_package: SourcePackage) -> Dict[str, SourcePackage]:
        """Return relevant packages to run autotests against for a given source package.

        Calculates the collection of reverse dependencies for a given
        source package that would be appropriate to re-run autopkgtests
        on, using the given @param source_package's name as a trigger.

        For leaf packages (that nothing else depends on as a build
        requirement), this routine returns an empty dict.

        For packages that can serve as an alternative dependency of some
        packages, this will include all such packages as if they were
        hard dependencies.  For example, when examining postgresql-12, this
        would include all packages dependent on any database.

        :param str source_package_name: The archive name of the source package.
        :rtype: dict[str, SourcePackage]
        :returns: Collection of source packages, keyed by name.
        """
        # Build the lookup table for provides and rdepends
        if not self._rdepends_table:
            if not self._rebuild_lookup_tables():
                raise RuntimeError("Could not regenerate provides/rdepends lookup tables")

        dependencies = {}

        # Get source packages that depend on things we supply
        for binary_package_name in source_package.provides_binaries.keys():
            rdeps = self._rdepends_table.get(binary_package_name)
            if rdeps:
                for rdep_source in rdeps:
                    dependencies[rdep_source.name] = rdep_source

        return dependencies


if __name__ == '__main__':
    # pylint: disable=invalid-name
    import sys
    from pprint import PrettyPrinter
    pp = PrettyPrinter(indent=4)

    from .repository import Repository
    from .debug import error

    print('############################')
    print('## Suite class smoke test ##')
    print('############################')
    print()

    local_dists_path = os.path.join(LOCAL_REPOSITORY_PATH, 'dists')
    if not os.path.exists(local_dists_path):
        error(f'Missing checkout for suite smoketest\n{LOCAL_REPOSITORY_MIRRORING_DIRECTIONS}')
        sys.exit(1)

    repository = Repository(cache_dir=local_dists_path)
    for suite in repository.suites.values():
        print(suite)
        print(f'  series:         {suite.series_codename}')
        print(f'  pocket:         {suite.pocket}')
        print(f'  components:     {", ".join(suite.components)}')
        print(f'  architectures:  {", ".join(suite.architectures)}')

        num_sources = len(suite.sources)
        ellipses_shown = False
        print(f'  sources:        ({num_sources} items)')
        for i, suite_source in enumerate(suite.sources):
            if i < 3 or i >= num_sources - 3:
                print(f'    {i} {suite_source}')
            elif not ellipses_shown:
                print('    [...]')
                ellipses_shown = True

        num_binaries = len(suite.binaries)
        ellipses_shown = False
        print(f'  binaries:       ({num_binaries} items)')
        for i, binary in enumerate(suite.binaries):
            if i < 3 or i >= num_binaries - 3:
                print(f'    {i} {binary}')
            elif not ellipses_shown:
                print('    [...]')
                ellipses_shown = True
