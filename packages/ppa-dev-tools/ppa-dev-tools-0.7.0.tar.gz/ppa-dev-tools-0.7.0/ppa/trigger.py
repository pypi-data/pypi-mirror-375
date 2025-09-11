#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Copyright (C) 2022-2024 Authors
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.
#
# Authors:
#   Bryce Harrington <bryce@canonical.com>

"""A directive to run a DEP8 test against a source package."""

from functools import lru_cache
from urllib.parse import urlencode
from typing import List

from .constants import URL_AUTOPKGTEST
from .text import ansi_hyperlink
from .source_publication import SourcePublication


class Trigger:
    """A publication and architecture to use when running an autopkgtest.

    A trigger indicates a source package whose autopkgtest(s) to invoke
    for a given hardware architecture, after installing a particular
    version of that package, and possibly other source packages, from a
    given series.

    A Job can have multiple Triggers, each against a different source
    package and/or architectures, but all such Triggers must be against
    the same series as the Job itself.
    """
    def __init__(self, source_publication, architecture, test_package=None):
        """Initialize a new Trigger for a given publication and architecture.

        :param SourcePublication source_publication: The source package
            publication object, which includes its name, version,
            series, and archive.
        :param str architecture: The hardware architecture to run on.
        :param str test_package: The package to run autopkgtests from.
        """
        self.source_publication = source_publication
        self.architecture = architecture
        if test_package:
            self.test_package = test_package
        else:
            self.test_package = source_publication.package

    def __repr__(self) -> str:
        """Return a machine-parsable unique representation of object.

        :rtype: str
        :returns: Official string representation of the object.
        """
        return (f'{self.__class__.__name__}('
                f'source_publication={self.source_publication!r}, '
                f'architecture={self.architecture!r}, '
                f'test_package={self.test_package!r})')

    def __str__(self) -> str:
        """Return a human-readable summary of the object.

        :rtype: str
        :returns: Printable summary of the object.
        """
        return f"{self.test_package}: {self.source_publication} [{self.architecture}]"

    @lru_cache
    def to_dict(self) -> dict:
        """Return a basic dict structure of the Trigger's data."""
        return {
            'source_publication': self.source_publication.to_dict(),
            'architecture': self.architecture,
            'test_package': self.test_package
        }

    @property
    @lru_cache
    def action_url(self) -> str:
        """Renders the trigger as a URL to start running the test.

        :rtype: str
        :returns: Trigger action URL
        """
        params = [
            ("release", self.source_publication.series),
            ("package", self.test_package),
            ("arch", self.architecture),
        ]

        # Trigger for the source package itself
        params.append(
            (
                "trigger",
                f"{self.source_publication.package}/{self.source_publication.version}")
            )

        # TODO: Additional triggers...

        # The PPA, if one is defined for this trigger
        if self.source_publication.archive:
            params.append(("ppa", self.source_publication.archive))

        return f"{URL_AUTOPKGTEST}/request.cgi?" + urlencode(params)


# TODO: Use SourcePub?
def get_triggers(package, version, ppa, series, architectures,
                 sources=None) -> List[Trigger]:
    """Returns Triggers for the given criteria.

    :param str package: The source package name.
    :param str version: The version of the source package to install.
    :param Ppa ppa: Archive containing the package to run tests against.
    :param str series: The distro release series codename.
    :param list[str] architectures: The architectures to provide triggers for.
    :param list[str] sources: (Unimplemented)
    :rtype: list[Trigger]
    :returns: List of triggers, if any, or an empty list on error.
    """
    source_pub = SourcePublication(package, version, series, archive=ppa)
    return [
        Trigger(source_pub, arch, sources)
        for arch
        in architectures
    ]


# TODO: Use SourcePub?
def show_triggers(triggers,
                  show_trigger_urls=False,
                  show_trigger_names=False):
    """Prints a list of triggers.

    :param list[Trigger] triggers:  The triggers to be displayed.
    :param str status: Result of the triggered test run.
    :param bool show_trigger_urls: If true, print out the trigger URLs
        as text; otherwise triggers will be printed as a hyperlink named
        'package/version'.  This is necessary for terminals lacking ANSI
        hyperlink support, for example.
    :param bool show_trigger_names: If true, includes display of the
        package names for triggers.  This may be useful if printing
        complex triggers or triggers for multiple different packages.
    """
    if show_trigger_urls:
        for trigger in triggers:
            title = ''
            arch = trigger.architecture
            if show_trigger_names:
                title = trigger.test_package
            print(f"    + {title}@{arch}: {trigger.action_url} ♻️ ")
        for trigger in triggers:
            title = ''
            arch = trigger.architecture
            if show_trigger_names:
                title = trigger.test_package
            url = trigger.action_url + "&all-proposed=1"
            print(f"    + {title}@{arch}: {url} 💍")

    else:
        for trigger in triggers:
            title = ''
            if show_trigger_names:
                title = trigger.test_package
            arch = trigger.architecture
            pad = ' ' * (1 + abs(len('ppc64el') - len(arch)))

            basic_trig = ansi_hyperlink(
                trigger.action_url, f"Trigger basic {title}@{arch}♻️ "
            )
            all_proposed_trig = ansi_hyperlink(
                trigger.action_url + "&all-proposed=1",
                f"Trigger all-proposed {title}@{arch}💍"
            )
            print("    + " + pad.join([basic_trig, all_proposed_trig]))


if __name__ == "__main__":
    import json

    print('##############################')
    print('## Trigger class smoke test ##')
    print('##############################')
    print()

    print("Basic trigger")
    print("-------------")
    pub = SourcePublication('my-package', '1.2.3', 'kinetic')
    t = Trigger(pub, 'amd64')
    print(pub)
    print(t)
    print(t.source_publication.autopkgtest_history_url)
    print(t.action_url)
    print()

    print("Object Dump")
    print("-----------")
    t = Trigger(pub, 'i386', 'ppa:me/myppa')
    print(json.dumps(t.to_dict(), indent=4))
    print()

    print("* PPA trigger:")
    pub = SourcePublication('my-ppa-package', '3.2.1', 'kinetic', 'my-ppa')
    t = Trigger(pub, 'amd64')
    print(t)
    print(t.source_publication.autopkgtest_history_url)
    print(t.action_url)
    print()
