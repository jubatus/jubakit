# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import jubatus
import jubatus.embedded

from .base import GenericSchema, BaseDataset, BaseService, GenericConfig
from .compat import *

class Schema(GenericSchema):
  """
  Schema for Anomaly service.
  """

  ID = 'i'
  FLAG = 'f'

  def __init__(self, mapping, fallback=None):
    self._id_key = self._get_unique_mapping(mapping, fallback, self.ID, 'ID', True)
    self._flag_key = self._get_unique_mapping(mapping, fallback, self.FLAG, 'FLAG', True)
    super(Schema, self).__init__(mapping, fallback)

  def transform(self, row):
    """
    Anomaly schema transforms the row into Datum, its associated ID and flag.
    Flag can be a value of any type.  It is provided for convenience to
    calculate precision.
    """
    row_id = row.get(self._id_key, None)
    if row_id is not None:
      row_id = unicode_t(row_id)
    row_flag = row.get(self._flag_key, None)
    d = self._transform_as_datum(row, None, [self._id_key, self._flag_key])
    return (row_id, row_flag, d)

class Dataset(BaseDataset):
  """
  Dataset for Anomaly service.
  """

  @classmethod
  def _predict(cls, row):
    return Schema.predict(row, False)

class Anomaly(BaseService):
  """
  Anomaly service.
  """

  @classmethod
  def name(cls):
    return 'anomaly'

  @classmethod
  def _client_class(cls):
    return jubatus.anomaly.client.Anomaly

  @classmethod
  def _embedded_class(cls):
    return jubatus.embedded.Anomaly

  def add(self, dataset):
    """
    Adds data points to the anomaly model using the given dataset and returns
    LOF scores.
    """
    cli = self._client()
    for (idx, (row_id, row_flag, d)) in dataset:
      if row_id is not None:
        raise RuntimeError('ID-based datasets must use `overwrite` or `update` instead of `add`')
      result = cli.add(d)
      yield (idx, result.id, row_flag, result.score)

  def update(self, dataset):
    """
    Updates data points in the anomaly model using the given dataset and
    returns LOF scores.
    """
    cli = self._client()
    for (idx, (row_id, row_flag, d)) in dataset:
      if row_id is None:
        raise RuntimeError('Non ID-based datasets must use `add` instead of `update`')
      result = cli.update(row_id, d)
      yield (idx, row_id, row_flag, result)

  def overwrite(self, dataset):
    """
    Overwrites data points in the anomaly model using the given dataset and
    returns LOF scores.
    """
    cli = self._client()
    for (idx, (row_id, row_flag, d)) in dataset:
      if row_id is None:
        raise RuntimeError('Non ID-based datasets must use `add` instead of `overwrite`')
      result = cli.overwrite(row_id, d)
      yield (idx, row_id, row_flag, result)

  def calc_score(self, dataset):
    """
    Calculates LOF scores for the given dataset.
    """
    cli = self._client()
    for (idx, (row_id, row_flag, d)) in dataset:
      result = cli.calc_score(d)
      yield (idx, row_id, row_flag, result)

class Config(GenericConfig):
  """
  Configuration to run Anomaly service.
  """

  @classmethod
  def methods(cls):
    return ['lof', 'light_lof']

  @classmethod
  def _default_method(cls):
    return 'lof'

  @classmethod
  def _default_parameter(cls, method):
    params = {
      'nearest_neighbor_num': 10,
      'reverse_nearest_neighbor_num': 30,
      'method': None,
      'parameter': {},
      'ignore_kth_same_point': True,
    }
    if method == 'lof':
      params['method'] = 'inverted_index_euclid'
    elif method == 'light_lof':
      params['method'] = 'euclid_lsh'
      params['parameter'] = {
        'threads': -1,  # use number of logical CPU cores
        'hash_num': 64,
      }
    else:
      raise RuntimeError('unknown method: {0}'.format(method))
    return params
