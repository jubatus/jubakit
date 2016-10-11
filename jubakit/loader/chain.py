# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from ..base import BaseLoader
from ..compat import *

"""
Chain loaders loads records from other loader(s).
"""

class MergeChainLoader(BaseLoader):
  """
  MergeChainLoader merges multiple loaders.
  """

  def __init__(self, *loaders):
    self._loaders = loaders

  def rows(self):
    for ent in zip_longest(*self._loaders, fillvalue={}):
      merged = {}
      for d in ent:
        merged.update(d)
      yield merged

class ValueMapChainLoader(BaseLoader):
  """
  ValueMapChainLoader is a loader to map value of the specified key in each
  record loaded from another loader.
  """

  def __init__(self, loader, key, mapping):
    self._loader = loader
    self._key = key
    self._mapping = mapping

  def rows(self):
    for ent in self._loader:
      ent[self._key] = self._mapping[ent[self._key]]
      yield ent

class ConcatLoader(BaseLoader):
  """
  ConcatLoader is a loader to concat multiple loaders.
  """
  def __init__(self, *loaders):
    self._loaders = loaders

  def rows(self):
    for loader in self._loaders:
      for row in loader.rows():
        yield row
