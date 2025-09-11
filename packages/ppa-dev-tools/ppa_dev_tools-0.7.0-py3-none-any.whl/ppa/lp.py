# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2021 Bryce W. Harrington
#
# Released under GNU AGPL or later, read the file 'LICENSE.AGPL' for
# more information.

# Extraction of bileto's lp class, for general use in other places

"""Launchpad Interface."""

from contextlib import suppress
from functools import lru_cache

from launchpadlib.launchpad import Launchpad
from launchpadlib.credentials import Credentials


class Lp:
    """High level wrapper object for Launchpad's API.

    This class wrappers the Launchpadlib service to cache object queries
    and to provide functionalies frequently needed when writing software
    for managing the Ubuntu distribution.

    This can be used as a drop-in replacement in scripts that already
    use Launchpadlib.  Simply replace your Launchpadlib.login_with() call
    with an instantiation of this class.  Any call that Lp does not handle
    itself is passed directly to the Launchpadlib object, so the entire
    API is available in exactly the same way.
    """
    # pylint: disable=invalid-name
    ROOT_URL = 'https://launchpad.net/'
    API_ROOT_URL = 'https://api.launchpad.net/devel/'
    BUGS_ROOT_URL = 'https://bugs.launchpad.net/'
    CODE_ROOT_URL = 'https://code.launchpad.net/'

    _real_instance = None

    def __init__(self, application_name, service=Launchpad,
                 staging=False, credentials=None, readonly=False):
        """Create a Launchpad service object.

        Authentication with Launchpad is done lazily, not at object
        initialization but at the point it first needs to actually use
        Launchpad functionality.  This permits adjustment of the
        object's credentials or other properties as needed.

        If the `$LP_CREDENTIAL` environment variable is defined, its
        contents will be loaded as the credentials to pass to the
        Credentials.from_string() function.  Stored credentials must
        be formatted according to the requirements of launchpadlib's
        Credentials class.  For more information on this class see:
            https://git.launchpad.net/launchpadlib/tree/src/launchpadlib/credentials.py

        :param str application_name: The text name of the software using
            this class.
        :param Launchpad service: The launchpadlib service class or
            object to wrapper.
        :param bool staging: When true, operate against a test instance
            of Launchpad instead of the real one.
        :param str credentials: (Optional) Formatted OAuth information
            to use when authenticating with Launchpad.  If not provided,
            will automatically login to Launchpad as needed.
        """
        self._app_name = application_name
        self._service = service
        self._credentials = credentials
        if staging:
            self._service_root = 'qastaging'
            self.ROOT_URL = 'https://qastaging.launchpad.net/'
            self.API_ROOT_URL = 'https://api.qastaging.launchpad.net/devel/'
            self.BUGS_ROOT_URL = 'https://bugs.qastaging.launchpad.net/'
            self.CODE_ROOT_URL = 'https://code.qastaging.launchpad.net/'
        else:
            self._service_root = 'production'
        if readonly:
            self._access_levels = ['READ_PUBLIC']
        else:
            self._access_levels = ['WRITE_PRIVATE']

    def _get_instance_from_creds(self) -> 'Launchpad | None':
        """
        Get an instance of _service using stored credentials if defined,
        else return None.

        For more information on Launchpad credentials-based authentication see
        https://help.launchpad.net/API/launchpadlib#Authenticated_access_for_website_integration

        :rtype: Launchpad | None
        :returns: Logged in Launchpad instance if credentials available,
            else None
        """
        if self._credentials:
            cred = Credentials.from_string(self._credentials)
            return self._service(
                cred, None, None,
                service_root=self._service_root,
                version='devel'
            )
        return None

    def _get_instance_from_login(self) -> 'Launchpad':
        """
        Prompts the user to authorize the login of a new credential
        or use the cached one if it is available and valid

        :rtype: launchpadlib.launchpad.Launchpad
        :returns: Logged in Launchpad instance
        """
        return self._service.login_with(
            application_name=self._app_name,
            service_root=self._service_root,
            allow_access_levels=self._access_levels,
            version='devel',  # Need devel for copyPackage.
        )

    @property
    def _instance(self):
        """Cache LP object."""
        if not self._real_instance:
            self._real_instance = (
                self._get_instance_from_creds() or
                self._get_instance_from_login()
            )
        return self._real_instance

    @property
    @lru_cache()
    def _api_root(self):
        """Identify the root URL of the launchpad API."""
        return self._instance.resource_type_link.split('#')[0]

    def __getattr__(self, attr):
        """Wrap launchpadlib so tightly you can't tell the difference."""
        assert not attr.startswith('_'), f"Can't getattr for {attr}"
        instance = super(Lp, self).__getattribute__('_instance')
        return getattr(instance, attr)

    @property
    @lru_cache()
    def ubuntu(self):
        """Shorthand for Ubuntu object.

        :rtype: distribution
        :returns: The distribution object for 'ubuntu'.
        """
        return self.distributions['ubuntu']

    @lru_cache()
    def ubuntu_active_series(self):
        """Identify currently supported Ubuntu series.

        This includes the series currently under development, but not
        ones which are experimental or obsolete.

        :rtype: list of distro_series
        :returns: All active Launchpad distro series for the Ubuntu project.
        """
        return [s for s in self.ubuntu.series if s.active]

    @lru_cache()
    def ubuntu_devel_series(self):
        """Identify the in-development Ubuntu series.

        This returns just the series currently under development or in a
        pre-release freeze.  While this is returned as a list for
        compatibility, there will typically be no more than one element
        in it.  However, note that this may be empty if used during the
        interim between a release and the opening of the next
        development series.

        :rtype: list of distro_series
        :returns: The in-development Launchpad distro series for the Ubuntu project.
        """
        devel_series = self.ubuntu.getDevelopmentSeries()
        if len(devel_series) > 0:
            return devel_series
        return [s for s in self.ubuntu.series if s.status == 'Pre-release Freeze']

    @lru_cache()
    def ubuntu_stable_series(self):
        """Identify current stable Ubuntu series.

        This includes the series considered stable currently.

        :rtype: distro_series
        :returns: All stable Launchpad distro series for the Ubuntu project.
        """
        return [s for s in self.ubuntu.series if s.status == 'Current Stable Release']

    @property
    @lru_cache()
    def debian(self):
        """Shorthand for Debian object.

        :rtype: distribution
        :returns: The distribution object for 'debian'.
        """
        return self.distributions['debian']

    @lru_cache()
    def debian_active_series(self):
        """Identify currently supported Debian series.

        :rtype: list of distro_series
        :returns: All active Launchpad distro series for the Debian project.
        """
        return [s for s in self.debian.series if s.active]

    @lru_cache()
    def debian_experimental_series(self):
        """Shorthand for Debian experimental series.

        :rtype: distro_series
        :returns: The Launchpad distro series for the Debian project.
        """
        return next(iter([s for s in self.debian.series if s.name == 'experimental']), None)

    @lru_cache()
    def get_teams(self, user):
        """Retrieve list of teams that user belongs to.

        :param str user: Name of the user to look up.
        :rtype: list(str)
        :returns: List of team names.
        """
        with suppress(KeyError, TypeError):
            return [
                team.self_link.partition('~')[-1].partition('/')[0]
                for team in self.people[user].memberships_details]

    def load(self, url):
        """Return a lp resource from a launchpad url.

        :param str url: The launchpad resource URL.
        :rtype: varies
        :returns: Launchpadlib object corresponding to given url.
        """
        return self._instance.load(url)
