# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import jubatus
import jubatus.embedded

from .base import GenericSchema, BaseDataset, BaseService, GenericConfig, Utils
from .loader.array import ArrayLoader, ZipArrayLoader
from .loader.sparse import SparseMatrixLoader
from .loader.chain import MergeChainLoader
from .compat import *

class Schema(GenericSchema):
  """
  Schema for Regression service.
  """

  TARGET = 't'

  def __init__(self, mapping, fallback=None):
    self._target_key = self._get_unique_mapping(mapping, fallback, self.TARGET, 'TARGET', True)
    super(Schema, self).__init__(mapping, fallback)

  def transform(self, row):
    """
    Regression schema transforms the row into Datum and its associated target value.
    """
    target = row.get(self._target_key, None)
    if target is not None:
      target = float(target)
    d = self._transform_as_datum(row, None, [self._target_key])
    return (target, d)

class Dataset(BaseDataset):
  """
  Dataset for Regression service.
  """

  @classmethod
  def _predict(cls, row):
    return Schema.predict(row, False)

  @classmethod
  def _from_loader(cls, data_loader, targets, static):
    if targets is None:
      loader = data_loader
      schema = Schema({}, Schema.NUMBER)
    else:
      # target is feeded with '_target' key from Loader.
      target_loader = ZipArrayLoader(_target=targets)
      loader = MergeChainLoader(data_loader, target_loader)
      schema = Schema({'_target': Schema.TARGET}, Schema.NUMBER)
    return Dataset(loader, schema, static)

  @classmethod
  def from_data(cls, data, targets=None, feature_names=None, static=True):
    """
    Converts two arrays or a sparse matrix data and its associated target array to Dataset.

    Parameters
    ----------
    data : array or scipy 2-D sparse matrix of shape [n_samples, n_features]
    targets : array of shape [n_samples], optional
    feature_names : array of shape [n_features], optional
    """
    if hasattr(data, 'todense'):
      return cls.from_matrix(data, targets, feature_names, static)
    else:
      return cls.from_array(data, targets, feature_names, static)

  @classmethod
  def from_array(cls, data, targets=None, feature_names=None, static=True):
    """
    Converts two arrays (data and its associated targets) to Dataset.

    Parameters
    ----------
    data : array of shape [n_samples, n_features]
    targets : array of shape [n_samples], optional
    feature_names : array of shape [n_features], optional
    """
    data_loader = ArrayLoader(data, feature_names)
    return cls._from_loader(data_loader, targets, static)

  @classmethod
  def from_matrix(cls, data, targets=None, feature_names=None, static=True):
    """
    Converts a sparse matrix data and its associated target array to Dataset.

    Parameters
    ----------

    data : scipy 2-D sparse matrix of shape [n_samples, n_features]
    targets : array of shape [n_samples], optional
    feature_names : array of shape [n_features], optional
    """
    data_loader = SparseMatrixLoader(data, feature_names)
    return cls._from_loader(data_loader, targets, static)

class Regression(BaseService):
  """
  Regression service.
  """

  @classmethod
  def name(cls):
    return 'regression'

  @classmethod
  def _client_class(cls):
    return jubatus.regression.client.Regression

  @classmethod
  def _embedded_class(cls):
    return jubatus.embedded.Regression

  def train(self, dataset):
    """
    Trains the regression using the given dataset.
    """
    cli = self._client()
    for (idx, (target, d)) in dataset:
      if target is None:
        raise RuntimeError('Dataset without target column cannot be used for training')
      result = cli.train([jubatus.regression.types.ScoredDatum(target, d)])
      assert result == 1
      yield (idx, target)

  def estimate(self, dataset):
    """
    Estimate target values of the given dataset using this Regression.
    """
    cli = self._client()
    for (idx, (target, d)) in dataset:
      # Do regression for the record.
      result = cli.estimate([d])
      assert len(result) == 1
      yield (idx, target, result[0])

  @classmethod
  def train_and_estimate(cls, config, train_dataset, test_dataset, metric):
    """
    This is an utility method to perform bulk train-test.
    Run a regression using the given config, train the regression,
    estimate using the regression, then return the calculated metrics.
    """
    regression = cls.run(config)

    for _ in regression.train(train_dataset):
      pass

    y_true = []
    y_pred = []
    for (idx, target, result) in regression.estimate(test_dataset):
      y_true.append(target)
      y_pred.append(result)

    regression.stop()

    return metric(y_true, y_pred)

class Config(GenericConfig):
    """
    Configulation to run Classifier service.
    """

    @classmethod
    def methods(cls):
      return ['perceptron', 'PA', 'PA1', 'PA2', 'CW', 'AROW', 'NHERD', 'NN', 'cosine', 'euclidean']

    @classmethod
    def _default_method(cls):
      return 'AROW'

    @classmethod
    def _default_parameter(cls, method):
      if method in ('perceptron'):
        return {'learning_rate': 1.0}
      elif method in ('PA', 'passive_aggressive'):
        return {'sensitivity': 1.0}
      elif method in ('PA1', 'passive_aggressive_1',
                      'PA2', 'passive_aggressive_2',
                      'CW', 'confidence_weighted',
                      'AROW',
                      'NHERD', 'normal_herd'):
        return {
          'sensitivity': 1.0,
          'regularization_weight': 1.0
        }
      elif method in ('cosine', 'euclidean'):
        return {'nearest_neighbor_num': 128}
      elif method in ('NN', 'nearest_neighbor'):
        return {
          'method': 'euclid_lsh',
          'parameter': {
            'threads': -1,
            'hash_num': 64
          },
          'nearest_neighbor_num': 128,
        }
      else:
        raise RuntimeError('unknown method: {0}'.format(method))
