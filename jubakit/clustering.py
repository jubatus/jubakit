# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import uuid

import jubatus
import jubatus.embedded

from .base import GenericSchema, BaseDataset, BaseService, GenericConfig, Utils
from .loader.array import ArrayLoader, ZipArrayLoader
from .loader.sparse import SparseMatrixLoader
from .loader.chain import ValueMapChainLoader, MergeChainLoader
from .compat import *

class Schema(GenericSchema):
  """
  Schema for Clustering service.
  """

  ID = 'i'

  def __init__(self, mapping, fallback=None):
    self._id_key = self._get_unique_mapping(mapping, fallback, self.ID, 'ID', True)
    super(Schema, self).__init__(mapping, fallback)

  def transform(self, row):
    """
    Clustering schema transforms the row into Datum, its associated ID.
    """
    row_id = row.get(self._id_key, None)
    if row_id is not None:
      row_id = unicode_t(row_id)
    else:
      row_id = unicode_t(uuid.uuid4())
    d = self._transform_as_datum(row, None, [self._id_key])
    return (row_id, d)

class Dataset(BaseDataset):
  """
  Dataset for Clustering service.
  """

  @classmethod
  def _predict(cls, row):
    return Schema.predict(row, False)

  @classmethod
  def _from_loader(cls, data_loader, ids, static):
    if ids is None:
      loader = data_loader
      schema = Schema({}, Schema.NUMBER)
    else:
      id_loader = ZipArrayLoader(_id=ids)
      loader = MergeChainLoader(data_loader, id_loader)
      schema = Schema({'_id': Schema.ID}, Schema.NUMBER)
    return Dataset(loader, schema, static)

  @classmethod
  def from_data(cls, data, ids=None, feature_names=None, static=True):
    """
    Converts two arrays or a sparse matrix data and its associated id array to Dataset.

    Parameters
    ----------
    data : array or scipy 2-D sparse matrix of shape [n_samples, n_features]
    ids : array of shape [n_samples], optional
    feature_names : array of shape [n_features], optional
    """

    if hasattr(data, 'todense'):
      return cls.from_matrix(data, ids, feature_names, static)
    else:
      return cls.from_array(data, ids, feature_names, static)

  @classmethod
  def from_array(cls, data, ids=None, feature_names=None, static=True):
    """
    Converts two arrays (data and its associated targets) to Dataset.

    Parameters
    ----------
    data : array of shape [n_samples, n_features]
    ids : array of shape [n_samples], optional
    feature_names : array of shape [n_features], optional
    """

    data_loader = ArrayLoader(data, feature_names)
    return cls._from_loader(data_loader, ids, static)

  @classmethod
  def from_matrix(cls, data, ids=None, feature_names=None, static=True):
    """
    Converts a sparse matrix data and its associated target array to Dataset.

    Parameters
    ----------

    data : scipy 2-D sparse matrix of shape [n_samples, n_features]
    ids : array of shape [n_samples], optional
    feature_names : array of shape [n_features], optional
    """

    data_loader = SparseMatrixLoader(data, feature_names)
    return cls._from_loader(data_loader, ids, static)

  def get_ids(self):
    """
    Returns labels of each record in the dataset.
    """

    if not self._static:
      raise RuntimeError('non-static datasets cannot fetch list of ids')
    for (idx, (row_id, d)) in self:
      yield row_id

class Clustering(BaseService):
  """
  Clustering service.
  """

  @classmethod
  def name(cls):
    return 'clustering'

  @classmethod
  def _client_class(cls):
    return jubatus.clustering.client.Clustering

  @classmethod
  def _embedded_class(cls):
    return jubatus.embedded.Clustering

  def push(self, dataset):
    """
    Add data points.
    """

    cli = self._client()
    for (idx, (row_id, d)) in dataset:
      if row_id is None:
        raise RuntimeError('each row must have `id`.')
      result = cli.push([jubatus.clustering.types.IndexedPoint(row_id, d)])
      yield (idx, row_id, result)

  def get_revision(self):
    """
    Return revision of clusters
    """

    cli = self._client()
    return cli.get_revision()

  def get_core_members(self, light=False):
    """
    Returns coreset of cluster in datum.
    This method support only kmeans and gmm.
    """

    cli = self._client()
    method = self._get_method()
    if method not in ('kmeans', 'gmm'):
      raise RuntimeError('{0} is not supported'.format(method))

    if light:
      return cli.get_core_members_light()
    else:
      return cli.get_core_members()

  def get_k_center(self):
    """
    Return k cluster centers.
    """

    cli = self._client()
    return cli.get_k_center()

  def get_nearest_center(self, dataset):
    """
    Returns nearest cluster center without adding points to cluster.
    """

    cli = self._client()
    method = self._get_method()
    if method not in ('kmeans', 'gmm'):
      raise RuntimeError('{0} is not supported'.format(method))

    for (idx, (row_id, d)) in dataset:
      result = cli.get_nearest_center(d)
      yield (idx, row_id, result)

  def get_nearest_members(self, dataset, light=False):
    """
    Returns nearest summary of cluster(coreset) from each point.
    """

    cli = self._client()
    method = self._get_method()
    if method not in ('kmeans', 'gmm'):
      raise RuntimeError('{0} is not supported'.format(method))

    for (idx, (row_id, d)) in dataset:
      if light:
        result = cli.get_nearest_members_light(d)
      else:
        result = cli.get_nearest_members(d)
      yield (idx, row_id, result)

  def _get_method(self):
    if self._backend is not None:
      if 'method' in self._backend.config:
        method = self._backend.config['method']
        return method
    return None

class Config(GenericConfig):
  """
  Configulation to run Clustering service.
  """

  def __init__(self, method=None, parameter=None,
               compressor_method=None, compressor_parameter=None,
               converter=None):
    super(Config, self).__init__(method, parameter, converter)
    if compressor_method is not None:
      self['compressor_method'] = compressor_method
      default_compressor_parameter = \
        self._default_compressor_parameter(compressor_method)
      if default_compressor_parameter is None:
        if 'compressor_parameter' in self:
          del self['compressor_parameter']
      else:
        self['compressor_parameter'] = default_compressor_parameter

    if compressor_parameter is not None:
      if 'compressor_parameter' in self:
        self['compressor_parameter'].update(compressor_parameter)
      else:
        self['compressor_parameter'] = parameter

  @classmethod
  def _default(cls, cfg):
    super(Config, cls)._default(cfg)

    compressor_method = cls._default_compressor_method()
    compressor_parameter = cls._default_compressor_parameter(compressor_method)

    if compressor_method is not None:
        cfg['compressor_method'] = compressor_method
    if compressor_parameter is not None:
        cfg['compressor_parameter'] = compressor_parameter

    return cfg

  @classmethod
  def _default_method(cls):
    return 'kmeans'

  @classmethod
  def _default_compressor_method(cls):
    return 'simple'

  @classmethod
  def _default_parameter(cls, method):
    if method in ('kmeans', 'gmm'):
      return {
        'k': 3,
        'seed': 0
      }
    elif method in ('dbscan'):
      return {
        'eps': 0.2,
        'min_core_point': 3
      }
    else:
      raise RuntimeError('unknown method: {0}'.format(method))

  @classmethod
  def _default_compressor_parameter(cls, method):
    if method in ('simple'):
      return {
        'bucket_size': 100
      }
    elif method in ('compressive'):
      return {
        'bucket_size': 100,
        'bucket_length': 2,
        'compressed_bucket_size': 100,
        'bicriteria_base_size': 10,
        'forgetting_factor': 0.0,
        'forgetting_threshold': 0.5,
        'seed': 0
      }
    else:
      raise RuntimeError('unknown method: {0}'.format(method))

  @classmethod
  def methods(cls):
    return ['kmeans', 'gmm', 'dbscan']

  @classmethod
  def compressor_methods(cls):
    return ['simple', 'compressive']

