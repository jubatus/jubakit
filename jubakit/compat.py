# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import itertools
import shlex

try:
  # Python 3
  import builtins
except ImportError:
  # Python 2
  import __builtin__ as builtins

PYTHON2_6 = sys.version_info[:2] == (2, 6)
PYTHON3 = sys.version_info >= (3, 0)

zip_longest = itertools.zip_longest if PYTHON3 else itertools.izip_longest
unicode_t = str if PYTHON3 else unicode
long_t = int if PYTHON3 else long

def shell_split(s):
  if isinstance(s, unicode_t) and PYTHON2_6:
    # shlex does not support Unicode on Python 2.6
    return map(lambda x: x.decode(), shlex.split(s.encode()))
  return shlex.split(s)

if not PYTHON3:
  # Python 2.x
  range = xrange
  zip = itertools.izip
