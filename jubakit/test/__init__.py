# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['requireSklearn']

try:
  import numpy
  import scipy
  import sklearn
  sklearn_available = True
except ImportError:
  sklearn_available = False

try:
  from unittest import skipUnless
  def requireSklearn(target):
    return skipUnless(sklearn_available, 'requires scikit-learn')(target)
except ImportError:
  def requireSklearn(target):
    return target if sklearn_available else None
