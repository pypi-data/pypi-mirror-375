#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Copyright (C) 2022 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.
#
# Authors:
#   Bryce Harrington <bryce@canonical.com>

'''
Routines for dealing with dictionary objects.
'''


def unpack_to_dict(text, key_cut=':', key_sep='=') -> dict:
    """Convert comma-delimited data into a dictionary.

    For each item, if @param key_sep is present split on it to get the
    key and value.  If @param key_sep is not present, then the item will
    be stored as the key with an empty string as the value.

    The key is further processed by excluding anything after @param
    key_cut.  For example, with the default values for @param key_sep
    and @param key_cut, the string "a,b=1.2.3,c:xyz=42" will unpack
    into:

        {
            'a': '',
            'b': '1.2.3',
            'c': '42',
        }

    A basic use case of this routine is to split out comma-separated
    items in a command line parameter's value string.  The @param
    key_sep parameter facilitates parsing lists of key=value items.  The
    @param key_cut provides a mechanism for filtering out unwanted
    portions of key names; for example, in "mypackage/universe=1.2.3" we
    may want to ignore the 'universe' detail.

    This routine is intended to handle parsing of Debian control fields
    sufficiently to determine the package names.  This routine is NOT
    intended to be a specification-compliant parser, and in particular
    is neither idempotent nor thorough in its parsing.  See
    https://wiki.debian.org/BuildProfileSpec for details about Debian's
    control field format.

    To support these control fields, the '|' symbol is recognized as a
    way of representing multiple alternative items via a tuple of keys
    and a dict for the value.  For example, the string 'a,b=1|c=2,d=3'
    will unpack into:

        {
            'a': '',
            ('b', 'c'): {'b': '1', 'c': '2'},
            'd': '3'
        }

    :param str text: Comma-separated textual data collection.
    :param str key_cut: Ignore anything in key after this character.
    :param str key_sep: Character used to separate an item's key from its value.
    :returns: Dictionary of data->value items
    :rtype: dict[str, str]
    """
    if not text or not key_sep or not key_cut:
        # None is not handled for any of the parameters so far.
        raise ValueError("unpack_to_dict() requires non-None values for all arguments")
    elif key_sep.strip() == ',':
        # Comma is used internally as the separator character, and
        # cannot currently be configured differently, thus it can't be
        # used by key_sep as a secondary separator.
        raise ValueError("comma is reserved and cannot be used for key_sep")
    elif not key_cut.strip() or key_cut.strip() == ',':
        # Whitespace is permitted for key_sep, but not for key_cut.
        # Comma is not allowed for key_cut, for same reason as for key_sep.
        raise ValueError("key_cut must be at least one (non-comma, non-whitespace) character")
    elif key_sep.strip() == key_cut.strip():
        # Since we're splitting on key_sep, using the same string to then split
        # key_cut would be redundant and ineffective.
        raise ValueError("key_sep and key_cut must not be the same string")

    def _split_item(item, key_sep, key_cut):
        if key_sep in item:
            key, value = item.split(key_sep, 1)
        else:
            key = item
            value = ''
        if key_cut:
            key = key.split(key_cut, 1)[0]

        # Blank value is allowed, but not key.  Neither can be None.
        if not key or value is None:
            raise ValueError
        return key.strip(), value.strip()

    dictionary = {}
    for item in text.split(','):
        if not item:
            raise ValueError

        item = item.strip()
        if '|' in item:
            # Handled items with are actually multiple items OR-ed together.
            subitems = {}
            for subitem in item.split('|'):
                subitem = subitem.strip()
                if not subitem:
                    raise ValueError("Undefined element of OR ('|') clause")
                subitems.update(dict([_split_item(subitem, key_sep, key_cut)]))

            # Store multi-values using a tuple key rather than a simple string.
            dictionary[tuple(subitems.keys())] = subitems
        else:
            # Store single-values as a simple string key.
            dictionary.update(dict([_split_item(item, key_sep, key_cut)]))
    return dictionary


if __name__ == "__main__":
    # pylint: disable=line-too-long, invalid-name

    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    print('#####################')
    print('## Dict smoke test ##')
    print('#####################')
    print()

    text = "a, b=1.2.3, c:x=4"
    print(text)
    pp.pprint(unpack_to_dict(text))
    print()

    print("* Conflicts:")
    text = "binutils-mingw-w64-i686 (<< 2.23.52.20130612-1+3), zlib1g (>= 1:1.1.4)"
    print(text)
    pp.pprint(unpack_to_dict(text, key_sep=' '))
    print()

    print("* Build-Depends:")
    text = "autoconf (>= 2.64), dpkg-dev (>= 1.19.0.5), bison, flex, gettext, texinfo, dejagnu, quilt, chrpath, dwz, debugedit (>= 4.16), python3:any, file, xz-utils, lsb-release, zlib1g-dev, procps, g++-aarch64-linux-gnu [amd64 i386 x32] <!nocheck>, g++-arm-linux-gnueabi [amd64 arm64 i386 x32] <!nocheck>, g++-arm-linux-gnueabihf [amd64 arm64 i386 x32] <!nocheck>, g++-powerpc64le-linux-gnu [amd64 arm64 i386 ppc64 x32] <!nocheck>, g++-s390x-linux-gnu [amd64 arm64 i386 ppc64el x32] <!nocheck>, g++-alpha-linux-gnu [amd64 i386 x32] <!nocheck>, g++-hppa-linux-gnu [amd64 i386 x32] <!nocheck>, g++-m68k-linux-gnu [amd64 i386 x32] <!nocheck>, g++-powerpc-linux-gnu [amd64 i386 ppc64el x32] <!nocheck>, g++-powerpc64-linux-gnu [amd64 i386 x32] <!nocheck>, g++-riscv64-linux-gnu [amd64 arm64 i386 ppc64el x32] <!nocheck>, g++-sh4-linux-gnu [amd64 i386 x32] <!nocheck>, g++-sparc64-linux-gnu [amd64 i386 x32] <!nocheck>, g++-i686-linux-gnu [amd64 arm64 ppc64el x32] <!nocheck>, g++-x86-64-linux-gnu [arm64 i386 ppc64el] <!nocheck>, g++-x86-64-linux-gnux32 [amd64 arm64 i386 ppc64el] <!nocheck>"  # noqa: E501
    print(text)
    pp.pprint(unpack_to_dict(text, key_sep=' '))
    print()

    print("* Depends:")
    text = "binutils-common (= 2.38.50.20220707-1ubuntu1), libbinutils (= 2.38.50.20220707-1ubuntu1), binutils-x86-64-linux-gnu (= 2.38.50.20220707-1ubuntu1)"  # noqa: E501
    print(text)
    pp.pprint(unpack_to_dict(text, key_cut='#', key_sep=' '))
    print()

    print("* Depends:")
    text = """         adduser,
         libpam-runtime,
         lsb-base,
         openssl,
         ssl-cert,
         ucf,
         ${misc:Depends},
         ${shlibs:Depends}
         """
    print(text)
    pp.pprint(unpack_to_dict(text, key_cut='#', key_sep=' '))
    print()

    print("* Depends:")
    text = """         ${misc:Depends},
         debhelper-compat (= 13),
         dpkg-dev (>= 1.15.5),
         nginx-core (<< 5.1~) | nginx-light (<< 5.1~) | nginx-extras (<< 5.1~),
         nginx-core (>= 5) | nginx-light (>= 5) | nginx-extras (>= 5)
         """
    print(text)
    pp.pprint(unpack_to_dict(text, key_cut='#', key_sep=' '))
    print()

    print("* Depends:")
    text = """         ${misc:Depends},
         debhelper-compat (= 13),
         dpkg-dev (>= 1.15.5),
         nginx-core (<< 5.1~) | nginx-light (<< 5.1~) | nginx-extras (<< 5.1~),
         nginx-core (>= 5) | nginx-light (>= 5) | nginx-extras (>= 5)
         """
    print(text)
    pp.pprint(unpack_to_dict(text, key_sep=' ', key_cut='#'))
    print()
