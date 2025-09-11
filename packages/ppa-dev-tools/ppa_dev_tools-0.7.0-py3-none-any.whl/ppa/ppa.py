#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2019 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""A wrapper around a Launchpad Personal Package Archive object."""

import os
import re
import sys
import enum

from datetime import datetime
from functools import lru_cache
from itertools import chain
from typing import Iterator, List
from lazr.restfulclient.errors import BadRequest, NotFound, Unauthorized

from .constants import URL_AUTOPKGTEST, DISTRO_UBUNTU_POCKETS
from .io import open_url
from .job import Job, get_waiting, get_running
from .result import get_results
from .source_publication import SourcePublication


class PendingReason(enum.Enum):
    """This describes the reason that leads an operation to hang"""
    BUILD_FAILED = enum.auto()  # Build failed
    BUILD_WAITING = enum.auto()  # Build is still ongoing
    BUILD_PUB_WAITING = enum.auto()  # Build is awaiting publication
    SOURCE_PUB_WAITING = enum.auto()  # Source is awaiting publication
    BUILD_MISSING = enum.auto()  # Build was expected, but missing


class PpaNotFoundError(Exception):
    """Exception indicating a requested PPA could not be found."""

    def __init__(self, ppa_name, owner_name, message=None):
        """Initialize the exception object.

        :param str ppa_name: The name of the missing PPA.
        :param str owner_name: The person or team the PPA belongs to.
        :param str message: An error message.
        """
        self.ppa_name = ppa_name
        self.owner_name = owner_name
        self.message = message

    def __str__(self):
        """Return a human-readable error message.

        :rtype str:
        :return: Error message about the failure.
        """
        if self.message:
            return self.message
        return f"The PPA '{self.ppa_name}' does not exist for person or team '{self.owner_name}'"


class Ppa:
    """Encapsulate data needed to access and conveniently wrap a PPA.

    This object proxies a PPA, allowing lazy initialization and caching
    of data from the remote.
    """

    BUILD_FAILED_FORMAT = (
        "  - {package_name} ({version}) {arch} {state}\n"
        "    + Log Link: {log_link}\n"
        "    + Launchpad Build Page: {build_page}\n"
    )

    def __init__(self, ppa_name, owner_name, ppa_description=None, service=None):
        """Initialize a new Ppa object for a given PPA.

        This creates only the local representation of the PPA, it does
        not cause a new PPA to be created in Launchpad.  For that, see
        PpaGroup.create()

        :param str ppa_name: The name of the PPA within the owning
            person or team namespace.
        :param str owner_name: The name of the person or team the PPA
            belongs to.
        :param str ppa_description: Optional description text for the PPA.
        :param launchpadlib.service service: The Launchpad service object.
        """
        if not ppa_name:
            raise ValueError("undefined ppa_name.")
        if not owner_name:
            raise ValueError("undefined owner_name.")

        self.ppa_name = ppa_name
        self.owner_name = owner_name
        if ppa_description is None:
            self.ppa_description = ''
        else:
            self.ppa_description = ppa_description
        self._service = service

    def __repr__(self) -> str:
        """Return a machine-parsable unique representation of object.

        :rtype: str
        :returns: Official string representation of the object.
        """
        return (f'{self.__class__.__name__}('
                f'ppa_name={self.ppa_name!r}, owner_name={self.owner_name!r})')

    def __str__(self) -> str:
        """Return a displayable string identifying the PPA.

        :rtype: str
        :returns: Displayable representation of the PPA.
        """
        return f"{self.owner_name}/{self.name}"

    @property
    @lru_cache
    def archive(self):
        """Retrieve the LP Archive object from the Launchpad service.

        :rtype: archive
        :returns: The Launchpad archive object.
        :raises PpaNotFoundError: Raised if a PPA does not exist in Launchpad.
        """
        if not self._service:
            raise AttributeError("Ppa object not connected to the Launchpad service")
        try:
            owner = self._service.people[self.owner_name]
            return owner.getPPAByName(name=self.ppa_name)
        except NotFound:
            raise PpaNotFoundError(self.ppa_name, self.owner_name)

    @lru_cache
    def exists(self) -> bool:
        """Indicate if the PPA exists in Launchpad."""
        try:
            self.archive
            return True
        except PpaNotFoundError:
            return False

    @property
    @lru_cache
    def address(self):
        """The proper identifier of the PPA.

        :rtype: str
        :returns: The full identification string for the PPA.
        """
        return "ppa:{}/{}".format(self.owner_name, self.ppa_name)

    @property
    def name(self):
        """The name portion of the PPA's address.

        :rtype: str
        :returns: The name of the PPA.
        """
        return self.ppa_name

    @property
    def url(self):
        """The HTTP url for the PPA in Launchpad.

        :rtype: str
        :returns: The url of the PPA.
        """
        return self.archive.web_link

    @property
    def description(self):
        """The description body for the PPA.

        :rtype: str
        :returns: The description body for the PPA.
        """
        return self.ppa_description

    def set_description(self, description):
        """Configure the displayed description for the PPA.

        :rtype: bool
        :returns: True if successfully set description, False on error.
        """
        self.ppa_description = description
        try:
            archive = self.archive
        except PpaNotFoundError as e:
            print(e)
            return False
        archive.description = description
        retval = archive.lp_save()
        print("setting desc to '{}'".format(description))
        print("desc is now '{}'".format(self.archive.description))
        return retval and self.archive.description == description

    @property
    @lru_cache
    def is_private(self) -> bool:
        """Indicates if the PPA is private or public.

        :rtype: bool
        :returns: True if the archive is private, False if public.
        """
        return self.archive.private

    def set_private(self, private: bool):
        """Attempts to configure the PPA as private.

        Note that PPAs can't be changed to private if they ever had any
        sources published, or if the owning person or team is not
        permitted to hold private PPAs.

        :param bool private: Whether the PPA should be private or public.
        """
        if private is None:
            return
        self.archive.private = private
        self.archive.lp_save()

    @property
    @lru_cache
    def publish(self):
        return self.archive.publish

    def set_publish(self, publish: bool):
        if publish is None:
            return
        self.archive.publish = publish
        self.archive.lp_save()

    @property
    @lru_cache
    def architectures(self) -> List[str]:
        """The architectures configured to build packages in the PPA.

        :rtype: List[str]
        :returns: List of architecture names, or None on error.
        """
        try:
            return [proc.name for proc in self.archive.processors]
        except PpaNotFoundError as e:
            sys.stderr.write(e)
            return None

    def set_architectures(self, architectures: List[str]) -> bool:
        """Configure the architectures used to build packages in the PPA.

        Note that some architectures may only be available upon request
        from Launchpad administrators.  ppa.constants.ARCHES_PPA is a
        list of standard architectures that don't require permissions.

        :param List[str] architectures: List of processor architecture names
        :rtype: bool
        :returns: True if architectures could be set, False on error or
            if no architectures were specified.
        """
        if not architectures:
            return False
        base = self._service.API_ROOT_URL.rstrip('/')
        procs = []
        for arch in architectures:
            procs.append(f'{base}/+processors/{arch}')
        try:
            self.archive.setProcessors(processors=procs)
            return True
        except PpaNotFoundError as e:
            sys.stderr.write(e)
            return False

    def set_pocket(self, pocket: str):
        f"""Configure the main archive dependency of the PPA to be against a given pocket.

        :param : str pocket: the targeted pocket (must be one of {DISTRO_UBUNTU_POCKETS})
        """

        if pocket not in DISTRO_UBUNTU_POCKETS:
            raise ValueError(f'{pocket} not in {DISTRO_UBUNTU_POCKETS}')

        main_archive = self.archive.distribution.main_archive
        # Using "multiverse" as a component as it matches the default value on the web UI.
        # See https://git.launchpad.net/launchpad/tree/lib/lp/soyuz/browser/archive.py#n1912
        self.archive.addArchiveDependency(
                component="multiverse",
                dependency=main_archive,
                pocket=pocket.title()
        )
        self.__class__.pocket.fget.cache_clear()

    @property
    @lru_cache
    def pocket(self):
        """The target pocket for the dependency to the main archive."""
        main_archive = self.archive.distribution.main_archive
        for dep in self.archive.dependencies:
            if dep.dependency == main_archive:
                return dep.pocket.lower()
        # If unspecified, the pocket is '$release-updates'
        return 'updates'

    @property
    @lru_cache
    def dependencies(self) -> List[str]:
        """The additional PPAs configured for building packages in this PPA.

        :rtype: List[str]
        :returns: List of PPA addresses
        """
        ppa_addresses = []
        for dep in self.archive.dependencies:
            ppa_dep = dep.dependency
            ppa_addresses.append(ppa_dep.reference)
        return ppa_addresses

    def set_dependencies(self, ppa_addresses: List[str]):
        """Configure the additional PPAs used to build packages in this PPA.

        This removes any existing PPA dependencies and adds the ones
        in the corresponding list.  If any of these new PPAs cannot be
        found, this routine bails out without changing the current set.

        :param List[str] ppa_addresses: Additional PPAs to add
        """
        base = self._service.API_ROOT_URL.rstrip('/')
        new_ppa_deps = []
        for ppa_address in ppa_addresses:
            owner_name, ppa_name = ppa_address_split(ppa_address)
            new_ppa_dep = f'{base}/~{owner_name}/+archive/ubuntu/{ppa_name}'
            new_ppa_deps.append(new_ppa_dep)

        # TODO: Remove all existing dependencies
#        for ppa_dep in self.archive.dependencies:
#            the_ppa.removeArchiveDependency(ppa_dep)

        # TODO: Not sure what to pass here, maybe a string ala 'main'?
        component = None

        # TODO: Allow setting alternate pockets
        # TODO: Maybe for convenience it should be same as what's set for main archive?
        pocket = 'Release'

        for ppa_dep in new_ppa_deps:
            self.archive.addArchiveDependency(
                component=component,
                dependency=ppa_dep,
                pocket=pocket)
        # TODO: Error checking
        #       This can throw ArchiveDependencyError if the ppa_address does not fit the_ppa
        self.__class__.dependencies.fget.cache_clear()

    def get_binaries(
        self, distro=None, series=None, arch=None, created_since_date=None,
        name=None
    ):
        """Retrieve the binary packages available in the PPA.

        :param distribution distro: The Launchpad distribution object.
        :param str series: The distro's codename for the series.
        :param str arch: The hardware architecture.
        :param datetime created_since_date: Only return binaries that
            were created on or after this date.
        :param str name: Only return binaries with this name.
        :rtype: List[binary_package_publishing_history]
        :returns: List of binaries, or None on error
        """
        if distro is None and series is None and arch is None:
            try:
                return chain(
                    self.archive.getPublishedBinaries(
                        created_since_date=created_since_date, status="Pending",
                        binary_name=name),
                    self.archive.getPublishedBinaries(
                        created_since_date=created_since_date, status="Published",
                        binary_name=name))
            except PpaNotFoundError as e:
                print(e)
                return None

        # TODO: Use SourcePublication and retrieve binaries from it
        print("Unimplemented")
        return []

    def get_source_publications(
        self,
        series: 'str | None' = None,
        created_since_date: 'datetime | None' = None,
        name: 'str | None' = None
    ) -> "Iterator(SourcePublication) | None":
        """Retrieve the source packages in the PPA.

        :param str series: The distro codename for the series.
        :param datetime created_since_date: Only return source publications that
            were created on or after this date.
        :param str name: Only return publications for this source package.

        :rtype: Iterator(SourcePublication) | None
        :returns: Collection of source publications, or None on error.
        """
        try:
            # Iterate through the launchpad publications, filtering by
            # any provided criteria, and then return as SourcePackage objects.
            params = {
                'component_name': None,
                'created_since_date': created_since_date,
                'distro_series': None,
                'order_by_date': True,
                'version': None,
            }
            if name:
                params['source_name'] = name
                params['exact_match'] = True
            if series:
                distro = self.archive.distribution
                params['distro_series'] = distro.getSeries(name_or_version=series)
            for lp_publication in chain(
                self.archive.getPublishedSources(status="Pending", **params),
                self.archive.getPublishedSources(status="Published", **params)
            ):
                yield SourcePublication(
                    package=lp_publication.source_package_name,
                    version=lp_publication.source_package_version,
                    series=lp_publication.distro_series.name,
                    archive=self,
                    status=lp_publication.status,
                )
        except PpaNotFoundError as e:
            print(e)
            return None

        return None

    def destroy(self):
        """Delete the PPA.

        :rtype: bool
        :returns: True if PPA was successfully deleted, is in process of
            being deleted, no longer exists, or didn't exist to begin with.
            False if the PPA could not be deleted for some reason and is
            still existing.
        """
        try:
            return self.archive.lp_delete()
        except PpaNotFoundError as e:
            print(e)
            return True
        except BadRequest:
            # Will report 'Archive already deleted' if deleted but not yet gone
            # we can treat this as successfully destroyed
            return True

    def has_packages(self, created_since_date=None, name=None) -> bool:
        """Indicate whether the PPA has any source packages.

        :param created_since_date: Cutoff date for the search, None means no cutoff.
        :param name: Only return source packages with this name.

        :rtype: bool
        :returns: True if PPA contains packages, False if empty or doesn't exit.
        """
        return any(self.archive.getPublishedSources(
            created_since_date=created_since_date,
            source_name=name
        ))

    def pending_publications(
        self,
        created_since_date: 'datetime | None' = None,
        name: 'str | None' = None,
        logging: 'bool' = False
    ) -> 'List[PendingReason]':
        """
        Check for pending publications and returns a list of PendingReason.

        :param datetime created_since_date: Cutoff date for the search, None means no cutoff
        :param str name: Only return pending publications for this source package.

        :rtype: list[PendingReason]
        :returns: A list of PendingReason indicating the status of the
            pending publications. Empty means there are no pending
            publications.
        """
        pending_publication_sources = {}
        required_builds = {}
        pending_publication_builds = {}
        published_builds = {}

        for source_publication in self.get_source_publications(
                created_since_date=created_since_date,
                name=name
        ):
            if not source_publication.date_published:
                pending_publication_sources[source_publication.self_link] = source_publication

            # iterate over the getBuilds result with no status restriction to get build records
            for build in source_publication.getBuilds():
                required_builds[build.self_link] = build

        for binary_publication in self.get_binaries(
                created_since_date=created_since_date,
                name=name
        ):
            # Ignore failed builds
            build = binary_publication.build
            if build.buildstate != "Successfully built":
                continue
            # Skip binaries for obsolete sources
            source_publication = build.current_source_publication
            if source_publication is None:
                continue

            if binary_publication.status == "Pending":
                pending_publication_builds[binary_publication.build_link] = binary_publication
            elif binary_publication.status == "Published":
                published_builds[binary_publication.build_link] = binary_publication

        if not logging:
            os.system('clear')

        retval = []
        num_builds_waiting = (
            len(required_builds) - len(pending_publication_builds) - len(published_builds)
        )
        if num_builds_waiting != 0:
            num_build_failures = 0
            builds_waiting_output = ''
            builds_failed_output = ''
            for build in required_builds.values():
                if build.buildstate == "Successfully built":
                    continue
                elif build.buildstate == "Cancelled build":
                    continue
                elif build.buildstate == "Failed to build":
                    num_build_failures += 1
                    builds_failed_output += self.BUILD_FAILED_FORMAT.format(
                        package_name=build.source_package_name,
                        version=build.source_package_version,
                        arch=build.arch_tag,
                        state=build.buildstate,
                        log_link=build.build_log_url,
                        build_page=build.web_link)
                else:
                    builds_waiting_output += "  - {} ({}) {}: {}\n".format(
                        build.source_package_name,
                        build.source_package_version,
                        build.arch_tag,
                        build.buildstate)
            if num_builds_waiting <= num_build_failures:
                print("* Some builds have failed:")
                print(builds_failed_output)
                retval.append(PendingReason.BUILD_FAILED)
            elif builds_waiting_output != '':
                print("* Still waiting on these builds:")
                print(builds_waiting_output)
                retval.append(PendingReason.BUILD_WAITING)

        if len(pending_publication_builds) != 0:
            num = len(pending_publication_builds)
            print(f"* Still waiting on {num} build publications:")
            for pub in pending_publication_builds.values():
                print("  - {}".format(pub.display_name))
            retval.append(PendingReason.BUILD_PUB_WAITING)
        if len(pending_publication_sources) != 0:
            num = len(pending_publication_sources)
            print(f"* Still waiting on {num} source publications:")
            for pub in pending_publication_sources.values():
                print("  - {}".format(pub.display_name))
            retval.append(PendingReason.SOURCE_PUB_WAITING)
        if ((list(required_builds.keys()).sort() != list(published_builds.keys()).sort())):
            print("* Missing some builds")
            retval.append(PendingReason.BUILD_MISSING)

        if not retval:
            print("Successfully published all builds for all architectures")
        return retval

    def get_autopkgtest_waiting(
            self,
            releases: 'List[str] | None',
            sources: 'List[str] | None' = None
            ) -> Iterator[Job]:
        """Return iterator of queued autopkgtests for this PPA.

        See get_waiting() for details

        :param List[str] releases: The Ubuntu series codename(s), or None.
        :param List[str] sources: Only retrieve results for these
            source packages, or all if blank or None.
        :rtype: Iterator[Job]
        :returns: Currently waiting jobs, if any, or an empty list on error
        """
        response = open_url(f"{URL_AUTOPKGTEST}/queues.json", "waiting autopkgtests")
        if response:
            return get_waiting(response, releases=releases, sources=sources, ppa=str(self))
        return []

    def get_autopkgtest_running(
            self,
            releases: 'List[str] | None',
            sources: 'List[str] | None' = None
            ) -> Iterator[Job]:
        """Return iterator of queued autopkgtests for this PPA.

        See get_running() for details

        :param List[str] releases: The Ubuntu series codename(s), or None.
        :param List[str] packages: Only retrieve results for these
            source packages, or all if blank or None.
        :rtype: Iterator[Job]
        :returns: Currently running jobs, if any, or an empty list on error
        """
        response = open_url(f"{URL_AUTOPKGTEST}/static/running.json", "running autopkgtests")
        if response:
            return get_running(response, releases=releases, sources=sources, ppa=str(self))
        return []

    def get_autopkgtest_results(
            self,
            releases: 'List[str] | None',
            architectures: 'List[str] | None',
            sources: 'List[str] | None' = None
            ) -> Iterator[dict]:
        """Returns iterator of results from autopkgtest runs for this PPA.

        See get_results() for details

        :param list[str] releases: The Ubuntu series codename(s), or None.
        :param list[str] architectures: The hardware architectures.
        :param list[str] sources: Only retrieve results for these
            source packages, or all if blank or None.
        :rtype: Iterator[dict]
        :returns: Autopkgtest results, if any, or an empty list on error
        """
        results = []
        for release in releases:
            base_results_fmt = f"{URL_AUTOPKGTEST}/results/autopkgtest-%s-%s-%s/"
            base_results_url = base_results_fmt % (release, self.owner_name, self.name)
            response = open_url(f"{base_results_url}?format=plain")
            if response:
                trigger_sets = {}
                for result in get_results(
                        response=response,
                        base_url=base_results_url,
                        arches=architectures,
                        sources=sources):
                    trigger = ', '.join([str(r) for r in result.get_triggers()])
                    trigger_sets.setdefault(trigger, [])
                    trigger_sets[trigger].append(result)
                results.append(trigger_sets)
        return results


def ppa_address_split(ppa_address):
    """Parse an address for a PPA into its owner and name components.

    :param str ppa_address: A ppa name or address.
    :rtype: tuple(str, str)
    :returns: The owner name and ppa name as a tuple, or (None, None) on error.
    """
    owner_name = None

    if not ppa_address or len(ppa_address) < 2:
        return (None, None)
    if ppa_address.startswith('ppa:'):
        if '/' not in ppa_address:
            return (None, None)
        rem = ppa_address.split('ppa:', 1)[1]
        owner_name = rem.split('/', 1)[0]
        ppa_name = rem.split('/', 1)[1]
    elif ppa_address.startswith('http'):
        # Only launchpad PPA urls are supported
        m = re.search(
            r'https://launchpad\.net/~([^/]+)/\+archive/ubuntu/([^/]+)(?:/*|/\+[a-z]+)$',
            ppa_address)
        if not m:
            return (None, None)
        owner_name = m.group(1)
        ppa_name = m.group(2)
    elif '/' in ppa_address:
        owner_name = ppa_address.split('/', 1)[0]
        ppa_name = ppa_address.split('/', 1)[1]
    else:
        ppa_name = ppa_address

    if owner_name is not None:
        if len(owner_name) < 1:
            return (None, None)
        owner_name = owner_name.lower()

    if (ppa_name
        and not (any(x.isupper() for x in ppa_name))
        and ppa_name.isascii()
        and '/' not in ppa_name
        and len(ppa_name) > 1):
        return (owner_name, ppa_name)

    return (None, None)


def get_ppa(lp, config):
    """Retrieve the specified PPA from Launchpad.

    :param Lp lp: The Launchpad wrapper object.
    :param dict config: Configuration param:value map.
    :rtype: Ppa
    :returns: Specified PPA as a Ppa object.
    """
    return Ppa(
        ppa_name=config.get('ppa_name', None),
        owner_name=config.get('owner_name', None),
        service=lp)


if __name__ == "__main__":
    import pprint
    import random
    import string
    from .lp import Lp
    from .ppa_group import PpaGroup

    pp = pprint.PrettyPrinter(indent=4)

    print('##########################')
    print('## Ppa class smoke test ##')
    print('##########################')
    print()

    # pylint: disable-next=invalid-name
    rndstr = str(''.join(random.choices(string.ascii_lowercase, k=6)))
    dep_name = f'dependency-ppa-{rndstr}'
    smoketest_ppa_name = f'test-ppa-{rndstr}'

    lp = Lp('smoketest', staging=True)
    ppa_group = PpaGroup(service=lp, name=lp.me.name)

    dep_ppa = ppa_group.create(dep_name, ppa_description=dep_name)
    the_ppa = ppa_group.create(smoketest_ppa_name, ppa_description=smoketest_ppa_name)
    ppa_dependencies = [f'ppa:{lp.me.name}/{dep_name}']

    try:
        the_ppa.set_publish(True)

        if not the_ppa.exists():
            print("Error: PPA does not exist")
            sys.exit(1)
        the_ppa.set_description("This is a testing PPA and can be deleted")
        the_ppa.set_publish(False)
        the_ppa.set_architectures(["amd64", "arm64"])
        the_ppa.set_dependencies(ppa_dependencies)

        print()
        print(f"name:          {the_ppa.name}")
        print(f"address:       {the_ppa.address}")
        print(f"str(ppa):      {the_ppa}")
        print(f"reference:     {the_ppa.archive.reference}")
        print(f"self_link:     {the_ppa.archive.self_link}")
        print(f"web_link:      {the_ppa.archive.web_link}")
        print(f"description:   {the_ppa.description}")
        print(f"has_packages:  {the_ppa.has_packages()}")
        print(f"architectures: {'/'.join(the_ppa.architectures)}")
        print(f"dependencies:  {','.join(the_ppa.dependencies)}")
        print(f"url:           {the_ppa.url}")
        print()

    except BadRequest as e:
        print(f"Error: (BadRequest) {str(e.content.decode('utf-8'))}")
    except Unauthorized as e:
        print(f"Error: (Unauthorized) {e}")

    # pylint: disable-next=invalid-name
    answer = 'x'
    while answer not in ['y', 'n']:
        answer = input('Ready to cleanup (i.e. delete) temporary test PPAs? (y/n) ')
        answer = answer[0].lower()

    if answer == 'y':
        print("  Cleaning up temporary test PPAs...")
        the_ppa.destroy()
        dep_ppa.destroy()
        print("  ...Done")
