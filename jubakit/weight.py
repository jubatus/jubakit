# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import jubatus

from .base import GenericSchema, BaseDataset, BaseService, GenericConfig
from .compat import *

class Schema(GenericSchema):
  """
  Schema for Weight service.
  """
  pass

class Dataset(BaseDataset):
  """
  Dataset for Weight service.
  """

  @classmethod
  def _predict(cls, row):
    return Schema.predict(row, False)

class Weight(BaseService):
  """
  Weight service.
  """

  @classmethod
  def name(cls):
    return 'weight'

  @classmethod
  def _client_class(cls):
    return jubatus.weight.client.Weight

  def update(self, dataset):
    """
    Updates the weight using the given dataset and returns extracted feature vectors.
    """

    cli = self._client()
    for (idx, d) in dataset:
      result = cli.update(d)
      yield (idx, result)

  def calc_weight(self, dataset):
    """
    Returns extracted feature vectors, without modifying the weight model.
    """

    cli = self._client()
    for (idx, d) in dataset:
      result = cli.calc_weight(d)
      yield (idx, result)

class Config(GenericConfig):
  """
  Configuration to run Weight service.
  """

  @classmethod
  def methods(cls):
    return []

  @classmethod
  def _default_method(cls):
    return None

  @classmethod
  def _default_parameter(cls, method):
    return None
