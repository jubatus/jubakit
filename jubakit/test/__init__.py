# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['requireSklearn']

from jubakit.compat import PYTHON3

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
  def requirePython3(target):
    return skipUnless(PYTHON3, 'requires Python 3.x')(target)
except ImportError:
  def requireSklearn(target):
    return target if sklearn_available else None
  def requirePython3(target):
    return target if PYTHON3 else None
