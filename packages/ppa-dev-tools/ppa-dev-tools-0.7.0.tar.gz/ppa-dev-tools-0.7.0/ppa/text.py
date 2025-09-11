#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# Copyright (C) 2011-2012 Bryce Harrington <bryce@bryceharrington.org>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''Routines to encode or convert to and from text.'''

import sys
from decimal import Decimal
from functools import lru_cache


# Constants for ANSI codes
OSC8 = "\u001b]8"
ST = "\u001b\\"


@lru_cache
def quote(msg):
    """Similar to urllib.quote but for glibs' GMarkup.

    @param msg: string to quote
    @returns: quoted string
    """
    msg = msg.replace('&', '&amp;')
    msg = msg.replace('<', '&lt;')
    msg = msg.replace('>', '&gt;')
    return msg


@lru_cache
def o2str(obj):
    """Return string representation of various types of objects.

    Convert a unicode, decimal.Decimal, datetime object, etc. to a str.
    Converts lists and tuples of objects into lists of strings.
    """
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, bytes):
        return obj.decode("utf-8")
    elif isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, list) or isinstance(obj, tuple):
        new_list = []
        for item in obj:
            new_list.append(o2str(item))
        return new_list
    elif str(type(obj)) == "<type 'datetime.datetime'>":
        return obj.ctime()
    else:
        # print str(type(obj))
        return obj


@lru_cache
def to_bool(value):
    """Convert 'something' to boolean. Raises exception for invalid formats.

    Possible True  values: 1, True, '1', 'TRue', 'yes', 'y', 't'
    Possible False values: 0, False, None, [], {}, '', '0', 'faLse', 'no', 'n', 'f', 0.0
    """
    if isinstance(value, str):
        if value.lower() in ("yes", "y", "true", "t", "1"):
            return True
        if value.lower() in ("no", "n", "false", "f", "0", "none", ""):
            return False
        raise Exception('Invalid value for boolean conversion: ' + value)
    return bool(value)


@lru_cache
def o2float(value):
    '''Convert strings like 42%, 123M, 1.2B into floating point numbers.

    Returned values are in millions, so '1.2B' returns 1200
    '''
    if value is None:
        return 0.0
    elif type(value) is float:
        return value
    elif type(value) is int:
        return float(value)
    elif value == '--':
        return 0.0

    value = value.replace(',', '')
    last = value[len(value) - 1]
    if last == 'M':
        return float(value[:-1])
    elif last == 'B':
        return float(value[:-1]) * 1000
    elif last == '%':
        return float(value[:-1]) / 100.0
    elif last == ')' and value[0] == '(':
        return -1 * o2float(value[1:-1])

    try:
        return float(value)
    except ValueError:
        sys.stderr.write(f"ofloat: Could not convert '{value}' to float\n")
        raise


def ansi_hyperlink(url, text):
    """Format text into a hyperlink using ANSI escape codes.

    :ref: https://iterm2.com/documentation-escape-codes.html
    :ref: https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda

    :param str url: The linked action to load in a web browser.
    :param str text: The visible text to show.
    :rtype: str
    :returns: ANSI escape code sequence to display the hyperlink.
    """
    return f"{OSC8};;{url}{ST}{text}{OSC8};;{ST}"


if __name__ == "__main__":
    print('#####################')
    print('## Text smoke test ##')
    print('#####################')
    print()

    print(ansi_hyperlink("https://launchpad.net/ppa-dev-tools", "ppa-dev-tools"))
