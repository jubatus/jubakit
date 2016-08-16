# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import jubatus

from .base import GenericSchema, BaseDataset, BaseService, GenericConfig
from .loader.array import ArrayLoader, ZipArrayLoader
from .loader.sparse import SparseMatrixLoader
from .loader.chain import ValueMapChainLoader, MergeChainLoader
from .compat import *

class Schema(GenericSchema):
  """
  Schema for Recommender service.
  """

  ID = 'i'

  def __init__(self, mapping, fallback=None):
    self._id_key = self._get_unique_mapping(mapping, fallback, self.ID, 'ID', True)
    super(Schema, self).__init__(mapping, fallback)

  def transform(self, row):
    """
    Recommender schema transforms the row into Datum, its associated ID.
    """
    row_id = row.get(self._id_key, None)
    if row_id is not None:
      row_id = unicode_t(row_id)
    d = self._transform_as_datum(row, None, [self._id_key])
    return (row_id, d)

class Dataset(BaseDataset):
  """
  Dataset for Recommender service.
  """

  @classmethod
  def _predict(cls, row):
    return Schema.predict(row, False)

class Recommender(BaseService):
  """
  Recommender service.
  """

  @classmethod
  def name(cls):
    return 'recommender'

  @classmethod
  def _client_class(cls):
    return jubatus.recommender.client.Recommender

  def update_row(self, dataset):
    """
    Update data points to the recommender model using the given dataset.
    """
    cli = self._client()
    for (idx, (row_id, d)) in dataset:
      result = cli.update_row(row_id, d)
      yield (idx, row_id, result)

  def complete_row_from_id(self, dataset):
    """
    Returns data points from the row id in the recommender model, 
    with missing value completed by predicted value.
    """
    cli = self._client()
    for (idx, (row_id, d)) in dataset:
      if row_id is None:
        raise RuntimeError('Non ID-based datasets must use `complete_row_from_datum`')
      result = cli.complete_row_from_id(row_id)
      yield (idx, row_id, result) 

  def complete_row_from_datum(self, dataset):
    """
    Returns data points from the datum in the recommender model,
    with missing value completed by predicted value.
    """
    cli = self._client()
    for (idx, (row_id, d)) in dataset:
      if d is None:
        raise RuntimeError('Non Datum-based datasets must use `complete_row_from_id`')
      result = cli.complete_row_from_datum(d)
      yield (idx, row_id, result)

  def similar_row_from_id(self, dataset, size=10):
    """
    Returns similar data points from the row id in the recommender model.
    """
    cli = self._client()
    for (idx, (row_id, d)) in dataset:
      if row_id is None:
        raise RuntimeError('Non ID-based datasets must use `similar_row_from_datum`')
      result = cli.similar_row_from_id(row_id, size)
      yield (idx, row_id, result) 

  def similar_row_from_datum(self, dataset, size=10):
    """
    Returns similar data points from the datum in the recommender model.
    """
    cli = self._client()
    for (idx, (row_id, d)) in dataset:
      if d is None:
        raise RuntimeError('Non Datum-based datasets must use `similar_row_from_datum`')
      result = cli.similar_row_from_datum(d, size)
      yield (idx, row_id, result)
       
  def decode_row(self, dataset):
    """
    Returns data points in the row id.
    """
    cli = self._client()
    for (idx, (row_id, d)) in dataset:
      if row_id is None:
        raise RuntimeError('Each data in datasets must has `row_id`')
      result = cli.decode_row(row_id)
      yield (idx, row_id, result) 

class Config(GenericConfig):
  """
  Configuration to run Recommender service.
  """

  @classmethod
  def methods(cls):
    return ['lsh', 'euclid_lsh', 'minhash', 'inverted_index', 
            'inverted_index_euclid', 'nearest_neighbor_recommend']

  @classmethod
  def _default_method(cls):
    return 'lsh'

  @classmethod
  def _default_parameter(cls, method):
    if method in ('inverted_index', 'inverted_index_euclid'):
      return None
    elif method in ('minhash'):
      return {
        'hash_num': 128,        
      }
    elif method in ('lsh', 'euclid_lsh'):
      return {
        'hash_num': 128,
        'threads': -1,
      }
    elif method in ('nearest_neighbor_recommender'):
      return {
        'method': 'euclid_lsh',
        'parameter': {
          'threads': -1,  # use number of logical CPU cores
          'hash_num': 128,
        },
      }
    else:
      raise RuntimeError('unknown method: {0}'.format(method))
