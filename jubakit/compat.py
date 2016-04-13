# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import itertools

if sys.version_info < (3, 0):
  # Python 2.x
  range = xrange
  zip = itertools.izip
  zip_longest = itertools.izip_longest
else:
  # Python 3.x
  zip_longest = itertools.zip_longest
