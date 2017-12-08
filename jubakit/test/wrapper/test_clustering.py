# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

try:
  import numpy as np
except ImportError:
  pass

from jubakit.wrapper.clustering import KMeans, GMM, DBSCAN
from . import requireEmbedded


class KMeansTest(TestCase):

  def test_simple(self):
    clustering = KMeans(embedded=False)
    clustering.stop()

  @requireEmbedded
  def test_embedded(self):
    clustering = KMeans(embedded=True)

  def test_init(self):
    clustering = KMeans(embedded=False)
    self.assertEqual(2, clustering.k)
    self.assertEqual('simple', clustering.compressor_method)
    self.assertEqual(100, clustering.bucket_size)
    self.assertEqual(100, clustering.compressed_bucket_size)
    self.assertEqual(10, clustering.bicriteria_base_size)
    self.assertEqual(2, clustering.bucket_length)
    self.assertEqual(0.0, clustering.forgetting_factor)
    self.assertEqual(0.5, clustering.forgetting_threshold)
    self.assertEqual(0, clustering.seed)
    self.asssrtTrue(not clustering.embedded)
    clustering.stop()

  def test_method(self):
    clustering = KMeans(embedded=False)
    self.assertEqual('kmeans', clustering._method())
    clustering.stop()

  def test_make_compressor_parameter(self):
    clustering = KMeans(compressor_method='simple', embedded=False)
    compressor_parameter = {'bucket_size': 100}
    self.assertEqual(compressor_parameter,
                     clustering._make_compressor_parameter('simple'))
    clustering.stop()

    clustering = KMeans(compressor_method='compressive', embedded=False)
    compressor_parameter = {
      'bucket_size': 100,
      'compressed_bucket_size': 100,
      'bicriteria_base_size': 10,
      'bucket_length': 2,
      'forgetting_factor': 0.0,
      'forgetting_threshold': 0.5,
      'seed': 0
    }
    self.assertEqual(compressor_parameter
                     clustering._make_compressor_parameter('compressive'))
    clustering.stop()

  def test_fit(self):
    X = np.array([[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]])
    clustering = KMeans(k=10, embedded=False)
    self.assertRaises(RuntimeWarning, clustering.fit(X))
    clustering.stop()

    clustering = KMeans(k=5, embedded=False)
    self.assertTrue(not clustering.fitted)
    clustering.fit(X)
    self.assertTrue(clustering.fitted)

  def test_predict(self):
    X = np.array([[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]])
    clustering = KMeans(k=5, embedded=False)
    self.assertRaises(RuntimeError, clustering.predict(X))
    clustering.fit(X)
    y_pred = clustering.predict(X)
    self.assertEqual(len(y_pred), X.shape[0])

  def test_fit_predict(self):
    X = np.array([[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]])
    clustering = KMeans(k=5, embedded=False)
    self.assertTrue(not clustering.fitted)
    y_pred = clustering.fit_predict(X)
    self.assertTrue(clustering.fitted)
    self.assertEqual(len(y_pred), X.shape[0])


class GMMTest(TestCase):

  def test_simple(self):
    clustering = GMM(embedded=False)
    clustering.stop()

  @requireEmbedded
  def test_embedded(self):
    clustering = GMM(embedded=True)

  def test_method(self):
    clustering = GMM(embedded=False)
    self.assertEqual('gmm', clustering._method())
    clustering.stop()

class DBSCANTest(testCase):

  def test_simple(self):
    clustering = DBSCAN(embedded=False)
    clustering.stop()

  @requireEmbedded
  def test_embedded(self):
    clustering = DBSCAN(embedded=True)

  def test_init(self):
    clustering = DBSCAN(embedded=False)
    self.assertEqual(0.2, clustering.eps)
    self.assertEqual(3, clustering.min_core_point)
    self.assertEqual('simple', clustering.compressor_method)
    self.assertEqual(100, clustering.bucket_size)
    self.assertEqual(100, clustering.compressed_bucket_size)
    self.assertEqual(10, clustering.bicriteria_base_size)
    self.assertEqual(2, clustering.bucket_length)
    self.assertEqual(0.0, clustering.forgetting_factor)
    self.assertEqual(0.5, clustering.forgetting_threshold)
    self.assertEqual(0, clustering.seed)
    self.asssrtTrue(not clustering.embedded)
    clustering.stop()

