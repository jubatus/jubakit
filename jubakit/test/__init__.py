# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['requireSklearn']

import unittest

try:
  import numpy
  import scipy
  import sklearn
  sklearn_available = True
except ImportError:
  sklearn_available = False

def requireSklearn(target):
  return unittest.skipUnless(sklearn_available, 'requires scikit-learn')(target)
