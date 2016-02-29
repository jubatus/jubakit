# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from itertools import izip

from ..base import BaseLoader

class ArrayLoader(BaseLoader):
  """
  Loader to process array.
  """

  def __init__(self, array):
    self._array = array

  def __iter__(self):
    for ent in self._array:
      yield self.preprocess(ent)

class SupervisedArrayDataLoader(BaseLoader):
  """
  SupervisedArrayDataLoader is a loader to read from two arrays (samples
  and their associated targets.)  This loader is expected to be used for
  supervised training (classifier, regression etc.) datasets loaded or
  generated from scikit-learn.
  """

  def __init__(self, data, target, feature_names, target_name='', target_map=None):
    self._data = data
    self._target = target
    self._feature_names = feature_names
    self._target_name = target_name
    self._target_map = target_map

  def __iter__(self):
    for (d, t) in izip(self._data, self._target):
      if self._target_map is not None:
        t = self._target_map[t]
      ent = dict(zip(self._feature_names, d))
      ent.update({self._target_name: t})
      yield self.preprocess(ent)
