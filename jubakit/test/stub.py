# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

import jubatus

from jubakit.base import BaseLoader, BaseSchema, BaseDataset, BaseService, BaseConfig, GenericConfig

class StubLoader(BaseLoader):
  DATA = [1,2,3]

  def __iter__(self):
    for d in self.DATA:
      yield self.preprocess({'v': d})
      yield None  # None should be ignored by Dataset

class StubInfiniteLoader(BaseLoader):
  def is_infinite(self):
    return True

  def __iter__(self):
    d = 1
    while True:
      yield self.preprocess({'v': d})
      d += 1

class StubService(BaseService):
  @classmethod
  def name(cls):
    return '_stub'

  @classmethod
  def _client_class(cls):
    return jubatus.common.ClientBase

class StubConfig(BaseConfig):
  @classmethod
  def _default(cls, cfg):
    cfg['test'] = 1.0

class StubGenericConfig(GenericConfig):
  @classmethod
  def methods(cls):
    return ['test', 'test2']

  @classmethod
  def _default_method(cls):
    return 'test'

  @classmethod
  def _default_parameter(cls, method):
    if method == 'test':
      return None
    elif method == 'test2':
      return {'param1': 1, 'param2': 2}
