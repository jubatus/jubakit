# -*= coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

try:
  import numpy as np
  from scipy.sparse import csr_matrix
except importError:
  pass

from jubakit.regression import Schema, Dataset, Regression, Config
from jubakit.compat import *

from . import requireSklearn, requireEmbedded
from .stub import *

class SchemaTest(TestCase):
  def test_simple(self):
    schema = Schema({
      'k1': Schema.STRING,
      'k2': Schema.TARGET,
    })

    (target, d) = schema.transform({'k1': 'abc', 'k2': 1.0})
    self.assertEqual(target, 1.0)
    self.assertEqual({'k1': 'abc'}, dict(d.string_values))

    (target, d) = schema.transform({'k1': 'abc', 'k2': None})
    self.assertEqual(target, None)
    self.assertEqual({'k1': 'abc'}, dict(d.string_values))

  def test_without_target(self):
    # schema without target can be defined
    Schema({
      'k1': Schema.STRING,
    })

  def test_illegal_target(self):
    # schema with multiple targets
    self.assertRaises(RuntimeError, Schema, {
      'k1': Schema.TARGET,
      'k2': Schema.TARGET
    })

    # schema fallback set to target
    self.assertRaises(RuntimeError, Schema, {
      'k1': Schema.TARGET
    }, Schema.TARGET)

class DatasetTest(TestCase):
  def test_simple(self):
    loader = StubLoader()
    schema = Schema({'v': Schema.TARGET})
    ds = Dataset(loader, schema)
    for (idx, (target, d)) in ds:
      self.assertEqual(idx+1, target)
      self.assertEqual(0, len(d.string_values))
      self.assertEqual(0, len(d.num_values))
      self.assertEqual(0, len(d.binary_values))

  def test_predict(self):
    loader = StubLoader()
    dataset = Dataset(loader)  # predict
    self.assertEqual(['v', 1.0], dataset[0][1].num_values[0])

  @requireSklearn
  def test_from_data(self):
    # load from array format
    ds = Dataset.from_data(
        [ [10,20,30], [20,10,50], [40,10,30] ], # data
        [ 0,          1,          2          ], # targets
        ['k1', 'k2', 'k3'],                     # feature_names
    )

    expected_targets = [0, 1, 2]
    expected_k1s = [10, 20, 40]
    actual_targets = []
    actual_k1s = []
    for (idx, (target, d)) in ds:
      actual_targets.append(target)
      actual_k1s.append(dict(d.num_values)['k1'])

    self.assertEqual(expected_targets, actual_targets)
    self.assertEqual(expected_k1s, actual_k1s)

    # load from scipy.sparse format
    ds = Dataset.from_data(
      self._create_matrix(),    # data
      [ 0, 1, 2 ],              # targets
      [ 'k1', 'k2', 'k3'],      # feature_names
    )

    expected_targets = [0, 1, 2]
    expected_k1s = [1, None, 4]
    expected_k3s = [2, 3, 6]
    actual_targets = []
    actual_k1s = []
    actual_k3s = []
    for (idx, (target, d)) in ds:
      actual_targets.append(target)
      actual_k1s.append(dict(d.num_values).get('k1', None))
      actual_k3s.append(dict(d.num_values).get('k3', None))

    self.assertEqual(expected_targets, actual_targets)
    self.assertEqual(expected_k1s, actual_k1s)
    self.assertEqual(expected_k3s, actual_k3s)

  def test_from_array(self):
    ds = Dataset.from_array(
        [ [10,20,30], [20,10,50], [40,10,30] ], # data
        [ 0,          1,          2          ], # targets
        ['k1', 'k2', 'k3'],                     # feature_names
    )

    expected_targets = [0, 1, 2]
    expected_k1s = [10, 20, 40]
    actual_targets = []
    actual_k1s = []
    for (idx, (target, d)) in ds:
      actual_targets.append(target)
      actual_k1s.append(dict(d.num_values)['k1'])

    self.assertEqual(expected_targets, actual_targets)
    self.assertEqual(expected_k1s, actual_k1s)

  def test_from_array_without_target(self):
    ds = Dataset.from_array(
        [ [10,20,30], [20,10,50], [40,10,30] ], # data
        None,                                   # targets
        ['k1', 'k2', 'k3'],                     # feature_names
    )

    expected_targets = [None, None, None]
    expected_k1s = [10, 20, 40]
    actual_targets = []
    actual_k1s = []
    for (idx, (target, d)) in ds:
      actual_targets.append(target)
      actual_k1s.append(dict(d.num_values)['k1'])

    self.assertEqual(expected_targets, actual_targets)
    self.assertEqual(expected_k1s, actual_k1s)

  @requireSklearn
  def test_from_matrix(self):
    ds = Dataset.from_matrix(
      self._create_matrix(),    # data
      [ 0, 1, 2 ],              # targets
      [ 'k1', 'k2', 'k3'],      # feature_names
    )

    expected_targets = [0, 1, 2]
    expected_k1s = [1,None,4]
    expected_k3s = [2,3,6]
    actual_targets = []
    actual_k1s = []
    actual_k3s = []
    for (idx, (target, d)) in ds:
      actual_targets.append(target)
      actual_k1s.append(dict(d.num_values).get('k1', None))
      actual_k3s.append(dict(d.num_values).get('k3', None))

    self.assertEqual(expected_targets, actual_targets)
    self.assertEqual(expected_k1s, actual_k1s)
    self.assertEqual(expected_k3s, actual_k3s)

  def _create_matrix(self):
    """
    Create a sparse matrix:

    [[1, 0, 2],
     [0, 0, 3],
     [4, 5, 6]]
    """
    row = np.array([0, 0, 1, 2, 2, 2])
    col = np.array([0, 2, 2, 0, 1, 2])
    data = np.array([1, 2, 3, 4, 5, 6])
    return csr_matrix((data, (row, col)), shape=(3, 3))

class RegressionTest(TestCase):
  def test_simple(self):
    regression = Regression()

  @requireEmbedded
  def test_embedded(self):
    regression = Regression.run(Config(), embedded=True)

class ConfigTest(TestCase):
  def test_simple(self):
    config = Config()
    self.assertEqual('AROW', config['method'])

  def test_methods(self):
    config = Config()
    self.assertTrue(isinstance(config.methods(), list))

  def test_default(self):
    config = Config.default()
    self.assertEqual('AROW', config['method'])

  def test_method_param(self):
    self.assertTrue('learning_rate' in Config(method='perceptron')['parameter'])
    self.assertTrue('sensitivity' in Config(method='PA')['parameter'])
    self.assertTrue('sensitivity' in Config(method='PA1')['parameter'])
    self.assertTrue('regularization_weight' in Config(method='PA1')['parameter'])
    self.assertTrue('nearest_neighbor_num' in Config(method='NN')['parameter'])
    self.assertTrue('nearest_neighbor_num' in Config(method='cosine')['parameter'])
    self.assertTrue('nearest_neighbor_num' in Config(method='euclidean')['parameter'])

  def test_invalid_method(self):
    self.assertRaises(RuntimeError, Config._default_parameter, 'invalid_method')
