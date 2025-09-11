Releasing a New PPA Dev Tools Version
=====================================

Before you start
----------------

* Update local Git repository to the current `main` tip.  For a
  maintenance release (e.g. version 1.2.3), update to the current
  `stable-1.2` tip, instead.

* Doublecheck all new dependencies are specified in packaging
  $ grep -h import */* | sed 's/    //' | grep -vE '(import|from) (ppa|\.)' | sort -u

* Doublecheck the INSTALL.md file is still up to date

* See ppa/_version.py for the current version number:
  $ export LAST_RELEASE=$(grep ^__version__ ppa/_version.py | cut -d\' -f2)
  $ echo "${LAST_RELEASE}"

* Define the new version for the release:
  $ export VERSION="<MAJOR>.<MINOR>.<PATCH>"

* Write an entry in NEWS.md file with release notes
  - The git log can be referred to for changes worth mentioning:
    $ git log --stat v${LAST_RELEASE}..

  - If desired, a shortlog can be appended to the release announcement,
    to itemize all changes:
    $ git shortlog v${LAST_RELEASE}...

* Commit everything that needs included in the release.  These two
  commands should produce no output:
  $ git diff HEAD
  $ git log main...origin/main

* Verify the build system works without errors
  $ make build

* Verify the testsuite, lint, flake, etc. passes
  $ make check
  $ make coverage

* Verify the snapcraft config is ready
  $ snapcraft --debug
  $ rm *.snap

* Cleanup
  $ make clean
  $ git status --ignored


Generate the source release
---------------------------

* Set the version
  $ export RELEASE_SERIES="X.Y"
  $ export VERSION="X.Y.Z"
  $ export PREVIOUS_VERSION="X.Y-1.Z"
  $ make set-release-version

* Add a changelog entry
  $ dch -v "${VERSION}"

* Add the release collateral
  $ git commit NEWS.md ppa/_version.py pyproject.toml debian/changelog snap/snapcraft.yaml -m "Releasing ${VERSION}"
  $ git tag -a -m "PPA Dev Tools ${VERSION}" "v${VERSION}"

* Push the release
  $ git push origin main "v${VERSION}"

* Create the release directory
  $ cp -ir ../$(basename $(pwd)) ~/pkg/PpaDevTools/${RELEASE_SERIES}/ppa-dev-tools-${VERSION}/
  $ cd ~/pkg/PpaDevTools/${RELEASE_SERIES}/ppa-dev-tools-${VERSION}

* Generate the release tarball
  $ make build
  $ gpg --armor --sign --detach-sig dist/*-${VERSION}*
  $ gpg --verify dist/ppa_dev_tools-${VERSION}.tar.gz.asc dist/ppa_dev_tools-${VERSION}.tar.gz
  $ python3 -m twine upload --verbose --repository pypi dist/*-${VERSION}*

* Generate the changelog
  $ git log v${PREVIOUS_VERSION}... > changelog.txt

* Generate the shortlog
  $ git shorlog v${PREVIOUS_VERSION}... > shortlog.txt


Generate the debian package
---------------------------

* Set to latest distro release, and add changelog entry for "New release"
  $ debuild -S -sa
  $ dput ppa:bryce/ppa-dev-tools ../ppa-dev-tools_${VERSION}_source.changes

* Repeat for each LTS release, with version set to ${VERSION}~YY.MM.N
  and changelog entry "Backport for ${codename}"
  $ distro-info --supported
  $ for series in $(distro-info --supported -c); do
      rel=$(distro-info -r --series=${series} | cut -d' ' -f1)
      n=1
      dch -i ...
      debuild -S -sa
      dput ppa:bryce/ppa-dev-tools ../ppa-dev-tools_${VERSION}~${rel}.${n}_source.changes
    done

Generate the snap
-----------------

* Build the snap locally
  $ make snap

* Verify the snap
  $ sudo snap install ppa-dev-tools_<version>_amd64.snap --devmode
  ppa-dev-tools <version> installed
  $ ppa --version
  ppa 0.6.0

* Push snap to the snap repository
  $ snapcraft upload --release edge *.snap



Announce release
----------------

* Add release announcement on Launchpad
* Send email to users' list
  - ppa-dev-tools-users@lists.launchpad.net
    CC ubuntu-devel <ubuntu-devel@lists.ubuntu.com>
    CC ubuntu-server <ubuntu-server@lists.ubuntu.com>
* Post to discourse Server channel, e.g. like
  https://discourse.ubuntu.com/t/release-of-ppa-dev-tools-0-4-0/35467


Return to Development
---------------------

* Add a final commit bumping the package version to a new development
  one
  - Set snapcraft.yaml back to version: git

* Finally, a manual `git push` (including tags) is required.
