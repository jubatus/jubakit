# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from ..base import BaseLoader
from ..compat import *

"""
Chain loaders loads records from other loader(s).
"""

class SupervisedDataChainLoader(BaseLoader):
  """
  SupervisedDataChainLoader is a loader to read from two loaders that provides
  feature vectors and its associated targets (ground truth).
  This loader is expected to be used for supervised training (classifier,
  regression etc.)
  """

  def __init__(self, data_loader, target_loader, target_map=None):
    self._data_loader = data_loader
    self._target_loader = target_loader
    self._target_map = target_map

  def __iter__(self):
    for (data, target) in zip_longest(self._data_loader, self._target_loader, fillvalue={}):
      if len(target) != 1:
        raise RuntimeError('target loader must provide 1-key record')

      (target_key, target_value) = list(target.items())[0]
      if self._target_map is not None:
        target_value = self._target_map[target_value]

      if target_key in data:
        raise RuntimeError('target key feeded from data loader')

      data[target_key] = target_value
      yield self.preprocess(data)
