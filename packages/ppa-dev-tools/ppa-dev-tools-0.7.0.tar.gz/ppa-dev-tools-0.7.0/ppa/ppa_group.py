#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2019 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""A person or team that owns one or more PPAs in Launchpad."""

from functools import lru_cache
from lazr.restfulclient.errors import BadRequest

from .ppa import Ppa
from .text import o2str


class PpaAlreadyExists(BaseException):
    """Exception indicating a PPA operation could not be performed."""

    def __init__(self, ppa_name, message=None):
        """Initialize the exception object.

        :param str ppa_name: The name of the pre-existing PPA.
        :param str message: An error message.
        """
        self.ppa_name = ppa_name
        self.message = message

    def __str__(self):
        """Return a human-readable error message.

        :rtype str:
        :return: Error message about the failure.
        """
        if self.message:
            return self.message
        elif self.ppa_name:
            return f"The PPA {self.ppa_name} already exists"


class PpaGroup:
    """Represents a person or team that owns one or more PPAs.

    This class provides a proxy object for interacting with collections
    of PPA.
    """

    def __init__(self, service, name):
        """Initialize a new PpaGroup object for a named person or team.

        :param launchpadlib.service service: The Launchpad service object.
        :param str name: Launchpad username for a person or team.
        """
        if not service:
            raise ValueError("undefined service.")
        if not name:
            raise ValueError("undefined name.")

        self.service = service
        self.name = name

    def __repr__(self):
        """Return a machine-parsable unique representation of object.

        :rtype: str
        :returns: Official string representation of the object.
        """
        return (f'{self.__class__.__name__}('
                f'service={self.service!r}, name={self.name!r})')

    def __str__(self):
        """Return a human-readable summary of the object.

        :rtype: str
        :returns: Printable summary of the object.
        """
        return 'tbd'

    @property
    @lru_cache
    def owner(self):
        """The person or team that owns this collection of PPAs.

        :rtype: launchpadlib.person
        :returns: Launchpad person object that owns this PPA.
        """
        return self.service.people[self.name]

    def create(self, ppa_name='ppa', ppa_description=None, private=False):
        """Register a new PPA with Launchpad.

        If a description is not provided a default one will be generated.

        :param str ppa_name: Name for the PPA to create.
        :param str ppa_description: Text description of the PPA.
        :param bool private: Limit access to PPA to only subscribed users and owner.
        :rtype: Ppa
        :returns: A Ppa object that describes the created PPA.

        :raises PpaAlreadyExists: Raised if a PPA by this name already exists in Launchpad.
        """
        ppa_settings = {
            'description': ppa_description,
            'displayname': ppa_name,
            'private': private
        }

        try:
            self.owner.createPPA(
                name=ppa_name,
                **ppa_settings
            )
            self.owner.lp_save()
        except BadRequest as e:
            if "You already have a PPA" in o2str(e.content):
                raise PpaAlreadyExists(ppa_name, e.content)
            else:
                raise e

        return Ppa(ppa_name, self.name, ppa_description, service=self.service)

    @property
    @lru_cache
    def ppas(self):
        """Generator to access the PPAs in this group.

        :rtype: Iterator[ppa.Ppa]
        :returns: Each PPA in the group as a ppa.Ppa object.
        """
        for lp_ppa in self.owner.ppas:
            if '-deletedppa' in lp_ppa.name:
                continue
            yield Ppa(lp_ppa.name, self.name,
                      service=self.service)

    @lru_cache
    def get(self, ppa_name):
        """Provide a Ppa for the named ppa.

        :rtype: ppa.Ppa
        :returns: A Ppa object describing the named ppa.
        """
        lp_ppa = self.owner.getPPAByName(name=ppa_name)
        if not lp_ppa:
            return None
        return Ppa(lp_ppa.name, self.name,
                   service=self.service)
