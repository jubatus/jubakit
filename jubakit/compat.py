# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import itertools

PYTHON3 = sys.version_info >= (3, 0)

zip_longest = itertools.zip_longest if PYTHON3 else itertools.izip_longest
unicode_t = str if PYTHON3 else unicode
long_t = int if PYTHON3 else long

if not PYTHON3:
  # Python 2.x
  range = xrange
  zip = itertools.izip
