#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Copyright (C) 2022 Authors
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.
#
# Authors:
#   Bryce Harrington <bryce@canonical.com>

"""An individual autopkgtest run."""

import json
from functools import lru_cache
from typing import Iterator
import urllib

from .constants import URL_AUTOPKGTEST


class Job:
    """An individual autopkgtest run that has not yet completed.

    A Job will correspond to one Result object once it has completed.
    """
    def __init__(self, number, submit_time, source_package, series, arch,
                 triggers=None, ppas=None):
        """Initialize a new Job object.

        :param str number: Position within the waiting queue.
        :param str submit_time: Timestamp when job was submitted.
        :param str source_package: Source package containing the DEP8 tests to run.
        :param str series: Codename of the Ubuntu release to run tests on.
        :param str arch: Hardware architecture type to run tests on.
        :param list[str] triggers: List of package/version triggers for the job.
        :param list[str] ppas: List of PPAs to enable.
        """
        self.number = number
        self.submit_time = submit_time
        self.source_package = source_package
        self.series = series
        self.arch = arch
        self.triggers = triggers or []
        self.ppas = ppas or []

    def __repr__(self) -> str:
        """Return a machine-parsable unique representation of object.

        :rtype: str
        :returns: Official string representation of the object.
        """
        return (f'{self.__class__.__name__}('
                f'source_package={self.source_package!r}, '
                f'series={self.series!r}, '
                f'arch={self.arch!r}'
                f')')

    def __str__(self) -> str:
        """Return a human-readable summary of the object.

        :rtype: str
        :returns: Printable summary of the object.
        """
        return f"{self.source_package} {self.series} ({self.arch})"

    @lru_cache
    def to_dict(self):
        return {
            'number': self.number,
            'submit_time': self.submit_time,
            'source_package_name': self.source_package,
            'series': self.series,
            'arch': self.series,
            'triggers': self.triggers,
            'ppas': self.ppas
        }

    @property
    def request_url(self) -> str:
        """Render URL for requesting the testing run be started.

        :rtype: str
        :returns: Full URL for invoking the test.
        """
        parameter_str = urllib.parse.urlencode({
            'release': self.series,
            'arch': self.arch,
            'package': self.source_package})
        for trigger in self.triggers:
            parameter_str += "&" + urllib.parse.urlencode({"trigger": trigger})
        return f"{URL_AUTOPKGTEST}/request.cgi?{parameter_str}"


def get_running(response, releases=None, sources=None, ppa=None) -> Iterator[Job]:
    """Return iterator currently running autopkgtests for given criteria.

    Filters the list of running autopkgtest jobs by the given series
    and/or ppa names, returning an iterator with matching results as Job
    objects.  If series and ppa are not provided, then returns all
    results; if one or the other is provided, provides all available
    results for that series or ppa.

    :param HTTPResponse response: Context manager; the response from urlopen()
    :param List[str] releases: The Ubuntu series codename(s), or None.
    :param List[str] sources: Only retrieve results for these
        source packages, or all if blank or None.
    :param str ppa: The PPA address criteria, or None.
    :rtype: Iterator[Job]
    :returns: Currently running jobs, if any, or an empty list on error
    """
    for pkg, jobs in json.loads(response.read().decode('utf-8') or '{}').items():
        if sources and (pkg not in sources):
            continue
        for handle in jobs:
            for codename in jobs[handle]:
                for arch, jobinfo in jobs[handle][codename].items():
                    triggers = jobinfo[0].get('triggers', None)
                    ppas = jobinfo[0].get('ppas', None)
                    submit_time = jobinfo[1]
                    job = Job(0, submit_time, pkg, codename, arch, triggers, ppas)
                    if releases and (job.series not in releases):
                        continue
                    if ppa and (ppa not in job.ppas):
                        continue
                    yield job


def get_waiting(response, releases=None, sources=None, ppa=None) -> Iterator[Job]:
    """Return iterator of queued autopkgtests for given criteria.

    Filters the list of autopkgtest jobs waiting for execution by the
    given series and/or ppa names, returning an iterator with matching
    results as Job objects.  If series and ppa are not provided, then
    returns all results; if one or the other is provided, provides all
    available results for that series or ppa.

    :param HTTPResponse response: Context manager; the response from urlopen()
    :param List[str] releases: The Ubuntu series codename(s), or None.
    :param List[str] sources: Only retrieve results for these
        source packages, or all if blank or None.
    :param str ppa: The PPA address criteria, or None.
    :rtype: Iterator[Job]
    :returns: Currently waiting jobs, if any, or an empty list on error
    """
    for _, queue in json.loads(response.read().decode('utf-8') or '{}').items():
        for codename in queue:
            for arch in queue[codename]:
                n = 0
                for key in queue[codename][arch]:
                    if key == 'private job':
                        continue
                    (pkg, json_data) = key.split(maxsplit=1)
                    if sources and (pkg not in sources):
                        continue
                    jobinfo = json.loads(json_data)
                    n += 1
                    triggers = jobinfo.get('triggers', None)
                    ppas = jobinfo.get('ppas', None)
                    job = Job(n, None, pkg, codename, arch, triggers, ppas)
                    if releases and (job.series not in releases):
                        continue
                    if ppa and (ppa not in job.ppas):
                        continue
                    yield job


def show_running(jobs):
    """Print the active (running and waiting) tests."""
    rformat = "%-8s %-20s %-8s %-8s %-25s %s"

    n = 0
    for n, e in enumerate(jobs, start=1):
        if n == 1:
            print("* Running:")
            t_str = str(e.submit_time)
            ppa_str = ','.join(e.ppas)
            trig_str = ','.join(e.triggers)
            print("  # " + rformat % ("time", "pkg", "release", "arch", "ppa", "trigger"))
        print("  - " + rformat % (t_str, e.source_package, e.series, e.arch, ppa_str, trig_str))
    if n == 0:
        print("* Running: (none)")


def show_waiting(jobs):
    """Print the active (running and waiting) tests."""
    rformat = "%-8s %-40s %-8s %-8s %-40s %s"

    n = 0
    for n, e in enumerate(jobs, start=1):
        if n == 1:
            print("* Waiting:")
            print("  # " + rformat % ("Q-num", "pkg", "release", "arch", "ppa", "trigger"))

        ppa_str = ','.join(e.ppas)
        trig_str = ','.join(e.triggers)
        print("  - " + rformat % (e.number, e.source_package, e.series, e.arch, ppa_str, trig_str))
    if n == 0:
        print("* Waiting: (none)")


if __name__ == "__main__":
    import os
    from urllib.request import urlopen

    print('############################')
    print('### Job class smoke test ###')
    print('############################')
    print()

    root_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
    jobinfo = {
        'triggers': ['a/1', 'b/2.1', 'c/3.2.1'],
        'ppas': ['ppa:me/myppa']
    }
    job_1 = Job(
        number=0,
        submit_time='time',
        source_package='my-package',
        series='kinetic',
        arch='amd64',
        triggers=jobinfo.get('triggers', None),
        ppas=jobinfo.get('ppas', None)
    )
    print(job_1)
    print(f"triggers:     {job_1.triggers}")
    print(f"ppas:         {job_1.ppas}")
    print(f"request_url:  {job_1.request_url}")
    print()

    # pylint: disable-next=invalid-name
    ppa = "bryce/dovecot-merge-v1e2.3.19.1adfsg1-2"

    print("running:")
    response = urlopen(f"file://{root_dir}/tests/data/running-20220822.json")
    for job in get_running(response, releases=['kinetic'], sources=None, ppa=ppa):
        print(job)
    print()

    print("waiting:")
    response = urlopen(f"file://{root_dir}/tests/data/queues-20220822.json")
    for job in get_waiting(response, releases=['kinetic'], sources=None, ppa=ppa):
        print(job)
    print()

    print("Object Dump")
    print("-----------")
    print(json.dumps(job_1.to_dict(), indent=4))
    print()
