#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2019 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

# pylint: disable=invalid-name

import os
import sys
from functools import lru_cache
from unittest.mock import Mock

from launchpadlib.credentials import Credentials

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.ppa import Ppa
from ppa.constants import ARCHES_PPA_DEFAULT
from ppa.ppa_group import PpaAlreadyExists


class SeriesMock:
    def __init__(self, name):
        self.name = name


class PublicationMock:
    def __init__(self, name, version, status, series):
        self.source_package_name = name
        self.source_package_version = version
        self.status = status
        self.distro_series = SeriesMock(series)


class ProcessorMock:
    """A stand-in for a Launchpad Processor object."""
    def __init__(self, name):
        self.name = name


class ArchiveDependencyMock:
    """A stand-in for a Launchpad ArchiveDependency object."""
    def __init__(self, archive, dependency, pocket, component):
        self.archive = archive
        self.dependency = dependency
        self.pocket = pocket
        self.component = component


class ArchiveMock:
    """A stand-in for a Launchpad Archive object."""
    def __init__(self, name, description, owner, distribution):
        self.displayname = name
        self.description = description
        self.owner = owner
        self.private = False
        self.processors = [ProcessorMock(proc_name) for proc_name in ARCHES_PPA_DEFAULT]
        self.publish = True
        self.published_sources = []
        self.published_binaries = []
        self.distribution = distribution
        self.dependencies = []
        self.web_link = None

    def setProcessors(self, processors):
        self.processors = [ProcessorMock(proc.split('/')[-1]) for proc in processors]

    def getPublishedSources(self, **params):
        return self.published_sources

    def getPublishedBinaries(self, **params):
        return self.published_binaries

    def lp_save(self):
        return True

    def addArchiveDependency(self, component=None, dependency=None, pocket=None):
        self.dependencies.append(ArchiveDependencyMock(self, dependency, pocket, component))


class PersonMock:
    """A stand-in for a Launchpad Person object."""
    def __init__(self, name):
        self.name = name
        self._ppas = []

    def createPPA(self, name, description, displayname, private=None):
        for ppa in self._ppas:
            if ppa.name == name:
                raise PpaAlreadyExists(name)
        ppa = Ppa(name, self.name, description)
        Ppa.archive = ArchiveMock(ppa.name, ppa.description, self, DEFAULT_DISTRO)
        if isinstance(private, bool):
            Ppa.archive.private = private
        self._ppas.append(ppa)
        return True

    def getPPAByName(self, name):
        for ppa in self._ppas:
            if ppa.name == name:
                return ppa.archive
        return None

    def lp_save(self):
        return True

    @property
    def ppas(self):
        return self._ppas


class DistributionMock:
    def __init__(self, name):
        self.name = name
        self.main_archive = ArchiveMock(
                "primary",
                "primary archive",
                PersonMock(f"{name}-archive"), self
        )

    def getSeries(self, name_or_version):
        return SeriesMock(name_or_version)


DEFAULT_DISTRO = DistributionMock('mydistro')


class LaunchpadMock:
    """A stand-in for Launchpad."""
    def __init__(self):
        self.people = {'me': PersonMock('me')}

    def add_person(self, name):
        print(f"Adding person {name}")
        self.people[name] = PersonMock(name)

    @property
    def me(self):
        return self.people['me']


class LpServiceMock:
    """A stand-in for the Lp service object."""
    ROOT_URL = 'https://mocklaunchpad.net/'
    API_ROOT_URL = 'https://api.mocklaunchpad.net/devel/'
    BUGS_ROOT_URL = 'https://bugs.mocklaunchpad.net/'
    CODE_ROOT_URL = 'https://code.mocklaunchpad.net/'

    def __init__(self, credentials=None):
        self.launchpad = LaunchpadMock()
        self._credentials = credentials

    @property
    @lru_cache
    def credentials(self):
        return Mock(Credentials)

    @property
    def me(self):
        return self.launchpad.people['me']

    @property
    def people(self):
        return self.launchpad.people

    def get_bug(self, bug_id):
        class BugMock:
            @property
            def title(self):
                return "Mock bug report"

            @property
            def description(self):
                return "Description line 1\n\ndescription line 2"

        return BugMock()


class RequestResponseMock:
    """A stand-in for a request result."""
    def __init__(self, text):
        self._text = text.encode('utf-8')

    def read(self):
        """Simply returns the exact text provided in initializer."""
        return self._text
