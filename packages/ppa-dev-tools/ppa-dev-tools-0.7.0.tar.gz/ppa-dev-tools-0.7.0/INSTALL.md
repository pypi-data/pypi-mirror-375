## Installation ##

The prerequisites for ppa-dev-tools can be satisified either through
PIP, or on Debian/Ubuntu via their packaging systems.

These modules are required:

  * appdirs
  * apt_pkg
  * debian.deb822
  * distro_info
  * launchpadlib
  * lazr.restfulclient
  * setuptools
  * software-properties
  * yaml or ruamel.yaml


### DEB ###

On Debian, ppa-dev-tools is available from the main archive, thus can be
installed directly:

  $ sudo apt-get install ppa-dev-tools


A PPA with .deb packages are available for Ubuntu.

  $ sudo add-apt-repository --yes --enable-source ppa:bryce/ppa-dev-tools
  $ sudo apt-get install ppa-dev-tools


### PIP ###

Alternatively, the package and its dependencies can be satisfied via PIP
for a user installation:

  $ pip install .
  $ ppa --version
  ppa 0.6.0


### SNAP ###

  $ sudo snap install ppa-dev-tools
  $ ppa --version
  ppa 0.6.0


### SOURCE ###

On Ubuntu 20.04 (or newer) and similar systems, prerequisites can be
satisfied from the apt repository:

  $ sudo apt-get install \
      python3-build \
      python3-appdirs \
      python3-debian \
      python3-distro-info \
      python3-launchpadlib \
      python3-lazr.restfulclient \
      python3-software-properties \
      python3-yaml \
      python3-pip

Installation is performed as follows:

  $ python3 -m build --no-isolation
  $ sudo python3 -m pip install --no-deps .
  $ ppa --version
  ppa 0.6.0
