# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import jubatus

from .base import BaseSchema, BaseDataset, BaseService, GenericConfig
from .loader.array import ArrayLoader, ZipArrayLoader
from .loader.sparse import SparseMatrixLoader
from .loader.chain import SupervisedDataChainLoader
from .compat import *

class Schema(BaseSchema):
  """
  Schema for Classifier service.
  """

  LABEL = 'label'

  def __init__(self, mapping, fallback=None):
    if fallback == self.LABEL:
      raise RuntimeError('label key cannot be specified as fallback schema')

    label_keys = [k for k in mapping.keys() if mapping[k] == self.LABEL]
    if len(label_keys) == 0:
      raise RuntimeError('label key is not specified in schema')
    elif 1 < len(label_keys):
      raise RuntimeError('label key must be unique in schema')

    self._label_key = label_keys[0]

    super(Schema, self).__init__(mapping, fallback)

  def transform(self, row):
    """
    Classifier schema transforms the row into Datum and its associated label.
    """
    label = row.get(self._label_key, None)
    d = self.transform_as_datum(row, None, [self._label_key])
    return (label, d)

class Dataset(BaseDataset):
  """
  Dataset for Classifier service.
  """

  @classmethod
  def _from_loaders(cls, data_loader, label_loader, label_names, static):
    loader = SupervisedDataChainLoader(data_loader, label_loader, label_names)
    schema = Schema({'_label': Schema.LABEL}, Schema.NUMBER)
    return Dataset(loader, schema, static)

  @classmethod
  def from_array(cls, data, labels, feature_names=None, label_names=None, static=True):
    """
    Converts two arrays (data and its associated labels) to Dataset.

    Parameters
    ----------
    data : array of shape [n_samples, n_features]
    labels : array of shape [n_samples]
    feature_names : array of shape [n_features], optional
    label_names : array of shape [n_labels], optional
    """
    # Label is feeded with '_label' key from Loader.
    return cls._from_loaders(
      ArrayLoader(data, feature_names),
      ZipArrayLoader(_label=labels),
      label_names,
      static,
    )

  @classmethod
  def from_matrix(cls, data, labels, feature_names=None, label_names=None, static=True):
    """
    Converts a sparse matrix data and its associated label array to Dataset.

    Parameters
    ----------

    data : scipy 2-D sparse matrix of shape [n_samples, n_features]
    labels : array of shape [n_samples]
    feature_names : array of shape [n_features], optional
    label_names : array of shape [n_labels], optional
    """
    # Label is feeded with '_label' key from Loader.
    return cls._from_loaders(
      SparseMatrixLoader(data, feature_names),
      ZipArrayLoader(_label=labels),
      label_names,
      static,
    )

  def get_labels(self):
    """
    Returns labels of each record in the dataset.
    """

    if not self._static:
      raise RuntimeException('non-static datasets cannot fetch list of labels')

    for (idx, (label, d)) in self:
      yield label

class Classifier(BaseService):
  """
  Classifier service.
  """

  @classmethod
  def name(cls):
    return 'classifier'

  @classmethod
  def _client_class(cls):
    return jubatus.classifier.client.Classifier

  def train(self, dataset):
    """
    Trains the classifier using the given dataset.
    """

    cli = self._client()
    for (idx, (label, d)) in dataset:
      assert label is not None
      result = cli.train([jubatus.classifier.types.LabeledDatum(unicode_t(label), d)])
      assert result == 1
      yield (idx, label)

  def classify(self, dataset):
    """
    Classify the given dataset using this classifier.
    """

    cli = self._client()
    for (idx, (label, d)) in dataset:
      # Do classification for the record.
      result = cli.classify([d])
      assert len(result) == 1

      # Create the list of (label, score) desc sorted by score.
      label_score_sorted = [(ent.label, ent.score) for ent in sorted(result[0], key=lambda x: x.score, reverse=True)]

      # Note: label may become None.
      yield (idx, label, label_score_sorted)

  @classmethod
  def train_and_classify(cls, config, train_dataset, test_dataset, metric):
    """
    This is an utility method to perform bulk train-test.
    Run a classifier using the given config, train the classifier, classify
    using the classifier, then return the calculated metrics.
    """
    classifier = cls.run(config)

    for _ in classifier.train(train_dataset):
      pass

    y_true = []
    y_pred = []
    for (idx, label, result) in classifier.classify(test_dataset):
      if 0 < len(result):
        y_true.append(label)
        y_pred.append(result[0][0])

    return metric(y_true, y_pred)

class Config(GenericConfig):
  """
  Configuration to run Classifier service.
  """

  @classmethod
  def methods(cls):
    return ['perceptron', 'PA', 'PA1', 'PA2', 'CW', 'AROW', 'NHERD', 'NN']

  @classmethod
  def _default_method(cls):
    return 'AROW'

  @classmethod
  def _default_parameter(cls, method):
    if method in ('perceptron',
                  'PA', 'passive_aggressive'):
      return None
    elif method in ('PA1', 'passive_aggressive_1',
                    'PA2', 'passive_aggressive_2',
                    'CW', 'confidence_weighted',
                    'AROW',
                    'NHERD', 'normal_herd'):
      return {'regularization_weight': 1.0}
    elif method in ('NN', 'nearest_neighbor'):
      return {
        'method': 'euclid_lsh',
        'parameter': {'hash_num': 64},
        'nearest_neighbor_num': 128,
        'local_sensitivity': 1.0
      }
    else:
      raise RuntimeError('unknown method: {0}'.format(method))
