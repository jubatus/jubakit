# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from ..base import BaseLoader
from ..compat import *

class ArrayLoader(BaseLoader):
  """
  ArrayLoader is a loader to read from 2-d array.
  Expected to load row-oriented data.

  For example:

  >>> ArrayLoader([[1,2,3], [4,5,6]], ['k1','k2','k3'])

  ... will load two entries:

    - {'k1': 1, 'k2': 2, 'k3': 3}
    - {'k1': 4, 'k2': 5, 'k3': 6}
  """

  def __init__(self, array, feature_names=None):
    if feature_names is None:
      feature_names = ['v{0}'.format(i) for i in range(len(array[0]))]

    self._array = array
    self._feature_names = feature_names

  def __iter__(self):
    for ent in self._array:
      yield self.preprocess(dict(filter(lambda x: x[1] is not None, zip(self._feature_names, ent))))

class ZipArrayLoader(BaseLoader):
  """
  ZipArrayLoader zips multiple 1-d arrays that have the same length.
  Expected to load column-oriented data.

  For example:

  >>> ZipArrayLoader([[1,4], [2,5], [3,6]], ['k1','k2','k3'])

  ... or simply:

  >>> ZipArrayLoader(k1=[1,4], k2=[2,5], k3=[3,6])

  ... will load two entries:

    - {'k1': 1, 'k2': 2, 'k3': 3}
    - {'k1': 4, 'k2': 5, 'k3': 6}
  """

  def __init__(self, arrays=[], feature_names=None, **named_arrays):
    if feature_names is None:
      feature_names = ['v{0}'.format(i) for i in range(len(arrays))]

    if len(arrays) != len(feature_names):
      raise RuntimeError('number of arrays and feature names mismatch')

    self._feature_names = feature_names
    self._arrays = list(arrays)
    for name in named_arrays:
      self._feature_names.append(name)
      self._arrays.append(named_arrays[name])

  def __iter__(self):
    for ent in zip(*self._arrays):
      yield self.preprocess(dict(filter(lambda x: x[1] is not None, zip(self._feature_names, ent))))
