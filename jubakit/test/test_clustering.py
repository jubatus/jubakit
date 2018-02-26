# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

try:
  import numpy as np
  from scipy.sparse import csr_matrix
except ImportError:
  pass

from jubakit.clustering import Schema, Dataset, Clustering, Config
from jubakit.compat import *

from . import requireSklearn, requireEmbedded
from .stub import *

class SchemaTest(TestCase):
  def test_simple(self):
    schema = Schema({
      'id': Schema.ID,
      'k1': Schema.STRING,
      'k2': Schema.NUMBER
    })
    (row_id, d) = schema.transform({'id': 'user001', 'k1': 'abc', 'k2': '123'})

    self.assertEqual(row_id, 'user001')
    self.assertEqual({'k1': 'abc'}, dict(d.string_values))
    self.assertEqual({'k2': 123}, dict(d.num_values))

  def test_without_id(self):
    # schema without id can be defined
    Schema({
      'k1': Schema.STRING,
    })

  def test_illegal_id(self):
    # schema with multiple IDs
    self.assertRaises(RuntimeError, Schema, {
      'k1': Schema.ID,
      'k2': Schema.ID,
    })

    # schema fallback set to id
    self.assertRaises(RuntimeError, Schema, {
      'k1': Schema.ID
    }, Schema.ID)

class DatasetTest(TestCase):
  def test_simple(self):
    loader = StubLoader()
    schema = Schema({'v': Schema.ID})
    ds = Dataset(loader, schema)
    for (idx, (label, d)) in ds:
      self.assertEqual(unicode_t(idx+1), label)
      self.assertEqual(0, len(d.string_values))
      self.assertEqual(0, len(d.num_values))
      self.assertEqual(0, len(d.binary_values))
    self.assertEqual(['1','2','3'], list(ds.get_ids()))

  def test_predict(self):
    loader = StubLoader()
    dataset = Dataset(loader)
    self.assertEqual(['v', 1.0], dataset[0][1].num_values[0])

  def test_from_data(self):
    # load from array format
    ds = Dataset.from_data(
      [ [10, 20, 30], [20, 10, 50], [40, 10, 30]],  # data
      ['i1', 'i2', 'i3'],                           # ids
      ['k1', 'k2', 'k3']                            # feature names
    )

    expected_k1s = [10, 20, 40]
    expected_ids = ['i1', 'i2', 'i3']
    actual_k1s = []
    actual_ids = []
    for (idx, (row_id, d)) in ds:
      actual_k1s.append(dict(d.num_values).get('k1', None))
      actual_ids.append(row_id)

    self.assertEqual(expected_k1s, actual_k1s)
    self.assertEqual(expected_ids, actual_ids)

    # load from scipy.sparse format
    ds = Dataset.from_data(
      self._create_matrix(),    # data
      ['i1', 'i2', 'i3'],       # ids
      [ 'k1', 'k2', 'k3'],      # feature_names
    )

    expected_k1s = [1, None, 4]
    expected_k3s = [2, 3, 6]
    expected_ids = ['i1', 'i2', 'i3']
    actual_k1s = []
    actual_k3s = []
    actual_ids = []
    for (idx, (row_id, d)) in ds:
      actual_k1s.append(dict(d.num_values).get('k1', None))
      actual_k3s.append(dict(d.num_values).get('k3', None))
      actual_ids.append(row_id)

    self.assertEqual(expected_k1s, actual_k1s)
    self.assertEqual(expected_k3s, actual_k3s)
    self.assertEqual(expected_ids, actual_ids)

  def test_from_array(self):
    ds = Dataset.from_array(
      [ [10, 20, 30], [20, 10, 50], [40, 10, 30]],  # data
      ['i1', 'i2', 'i3'],                           # ids
      ['k1', 'k2', 'k3']                            # feature names
    )

    expected_k1s = [10, 20, 40]
    expected_ids = ['i1', 'i2', 'i3']
    actual_k1s = []
    actual_ids = []
    for (idx, (row_id, d)) in ds:
      actual_k1s.append(dict(d.num_values).get('k1', None))
      actual_ids.append(row_id)

    self.assertEqual(expected_k1s, actual_k1s)
    self.assertEqual(expected_ids, actual_ids)

  def test_from_array_without_ids(self):
    ds = Dataset.from_array(
      [ [10, 20, 30], [20, 10, 50], [40, 10, 30]],  # data
      feature_names=['k1', 'k2', 'k3']              # feature names
    )

    expected_k1s = [10, 20, 40]
    actual_k1s = []
    actual_ids = []
    for (idx, (row_id, d)) in ds:
      actual_k1s.append(dict(d.num_values).get('k1', None))
      actual_ids.append(row_id)
    self.assertEqual(expected_k1s, actual_k1s)
    self.assertEqual(len(actual_ids), 3)

  @requireSklearn
  def test_from_matrix(self):
    ds = Dataset.from_matrix(
      self._create_matrix(),  # data
      ['i1', 'i2', 'i3'],     # ids
      ['k1', 'k2', 'k3']      # feature names
    )

    expected_k1s = [1, None, 4]
    expected_k3s = [2, 3, 6]
    expected_ids = ['i1', 'i2', 'i3']
    actual_k1s = []
    actual_k3s = []
    actual_ids = []
    for (idx, (row_id, d)) in ds:
      actual_k1s.append(dict(d.num_values).get('k1', None))
      actual_k3s.append(dict(d.num_values).get('k3', None))
      actual_ids.append(row_id)

    self.assertEqual(expected_k1s, actual_k1s)
    self.assertEqual(expected_k3s, actual_k3s)
    self.assertEqual(expected_ids, actual_ids)

  def test_get_ids(self):
    ds = Dataset.from_array(
      [ [10, 20, 30], [20, 10, 50], [40, 10, 30]],  # data
      ['i1', 'i2', 'i3'],                           # ids
      static=True
    )
    actual_ids = []
    expected_ids = ['i1', 'i2', 'i3']
    for row_id in ds.get_ids():
      actual_ids.append(row_id)
    self.assertEqual(expected_ids, actual_ids)

    ds = Dataset.from_array(
      [ [10, 20, 30], [20, 10, 50], [40, 10, 30]],  # data
      ['i1', 'i2', 'i3'],                           # ids
      static=False
    )
    self.assertRaises(RuntimeError, list, ds.get_ids())

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

class ClusteringTest(TestCase):
  def test_simple(self):
    clustering = Clustering()
    clustering.stop()

  @requireEmbedded
  def test_embedded(self):
    clustering = Clustering.run(Config(), embedded=True)
    clustering.stop()

  def test_push(self):
    clustering = Clustering.run(Config())
    dataset = self._make_stub_dataset()
    for (idx, row_id, result) in clustering.push(dataset):
      self.assertEqual(result, True)
    clustering.stop()

  def test_get_revision(self):
    clustering = Clustering.run(Config())
    self.assertEqual(0, clustering.get_revision())
    clustering.stop()

  def test_get_core_members(self):
    dataset = self._make_stub_dataset()
    config = Config(method='kmeans', compressor_parameter={"bucket_size": 5})
    clustering = self._make_stub_clustering(config, dataset)
    clustering.get_core_members(light=False)
    clustering.get_core_members(light=True)
    clustering.stop()

  def test_get_k_center(self):
    def func(clustering, dataset):
      clustering.get_k_center()
    self._test_func_with_legal_and_illegal_config(func)

  def test_get_nearest_center(self):
    def func(clustering, dataset):
      for _ in clustering.get_nearest_center(dataset): pass
    self._test_func_with_legal_and_illegal_config(func)

  def test_get_nearest_members(self):
    def func1(clustering, dataset):
      for _ in clustering.get_nearest_members(dataset, light=False): pass
    self._test_func_with_legal_and_illegal_config(func1)

    def func2(clustering, dataset):
      for _ in clustering.get_nearest_members(dataset, light=True): pass
    self._test_func_with_legal_and_illegal_config(func2)

  def _test_func_with_legal_and_illegal_config(self, func):
    dataset = self._make_stub_dataset()
    # test illegal method
    config = Config(method='dbscan', compressor_parameter={"bucket_size": 5})
    clustering = self._make_stub_clustering(config, dataset)
    self.assertRaises(RuntimeError, lambda: func(clustering, dataset))
    clustering.stop()

    # test legal method
    config = Config(method='kmeans', compressor_parameter={"bucket_size": 5})
    clustering = self._make_stub_clustering(config, dataset)
    func(clustering, dataset)
    clustering.stop()

  def _make_stub_clustering(self, config, dataset):
    dataset = self._make_stub_dataset()
    clustering = Clustering.run(config)
    for _ in clustering.push(dataset): pass
    return clustering

  def _make_stub_dataset(self):
    ids = ['id1', 'id2', 'id3', 'id4', 'id5']
    X = [
        [0, 0, 0],
        [1, 1, 1],
        [2, 2, 2],
        [3, 3, 3],
        [4, 4, 4]
    ]
    dataset = Dataset.from_array(X, ids=ids)
    return dataset


class ConfigTest(TestCase):
  def test_simple(self):
    config = Config()
    self.assertEqual('kmeans', config['method'])
    self.assertEqual({'k': 3, 'seed': 0}, config['parameter'])
    self.assertEqual('simple', config['compressor_method'])
    self.assertEqual({'bucket_size': 100}, config.get('compressor_parameter'))

  def test_methods(self):
    config = Config()
    self.assertTrue(isinstance(config.methods(), list))

  def test_compressor_methods(self):
    config = Config()
    self.assertTrue(isinstance(config.compressor_methods(), list))

  def test_illegal_comporessor_method(self):
    self.assertRaises(RuntimeError,
                      Config._default_compressor_parameter,
                      'invalid_compressor_method')

  def test_default(self):
    config = Config.default()
    self.assertEqual('kmeans', config['method'])
    self.assertEqual('simple', config['compressor_method'])

  def test_method_params(self):
    self.assertTrue('k' in Config(method='kmeans')['parameter'])
    self.assertTrue('seed' in Config(method='kmeans')['parameter'])
    self.assertTrue('k' in Config(method='gmm')['parameter'])
    self.assertTrue('seed' in Config(method='gmm')['parameter'])
    self.assertTrue('eps' in Config(method='dbscan')['parameter'])
    self.assertTrue('min_core_point' in Config(method='dbscan')['parameter'])

  def test_compressor_params(self):
    self.assertTrue('bucket_size' in
      Config(compressor_method='simple')['compressor_parameter'])
    self.assertTrue('bucket_size' in
      Config(compressor_method='compressive')['compressor_parameter'])
    self.assertTrue('bucket_length' in
      Config(compressor_method='compressive')['compressor_parameter'])
    self.assertTrue('compressed_bucket_size' in
      Config(compressor_method='compressive')['compressor_parameter'])
    self.assertTrue('bicriteria_base_size' in
      Config(compressor_method='compressive')['compressor_parameter'])
    self.assertTrue('forgetting_factor' in
      Config(compressor_method='compressive')['compressor_parameter'])
    self.assertTrue('seed' in
      Config(compressor_method='compressive')['compressor_parameter'])
    config = Config(compressor_method='simple',
                    compressor_parameter={'bucket_size': 10})
    self.assertEqual(10, config['compressor_parameter']['bucket_size'])

  def test_invalid_method(self):
    self.assertRaises(RuntimeError, Config._default_parameter, 'invalid_method')
