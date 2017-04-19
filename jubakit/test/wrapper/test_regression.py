# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

try:
  import numpy as np
except ImportError:
  pass

from jubakit.wrapper.regression import LinearRegression, NearestNeighborsRegression
from . import requireEmbedded


class LinearRegressionTest(TestCase):

  def test_simple(self):
    regression = LinearRegression()
    regression.stop()

  @requireEmbedded
  def test_embedded(self):
    regression = LinearRegression(embedded=True)

  @requireEmbedded
  def test_launch_regression(self):
    methods = ['AROW', 'CW', 'NHERD', 'PA', 'PA1', 'PA2', 'perceptron']
    def launch_regression(method):
      regression = LinearRegression(method=method)
      regression._launch_regression()
    for method in methods:
      self.assertEqual(launch_regression(method), None)
    self.assertRaises(NotImplementedError, launch_regression, 'Lasso')

  @requireEmbedded
  def test_partial_fit(self):
    X = np.array([[1,1], [0,0]])
    y = np.array([1,2])
    regression = LinearRegression()
    self.assertTrue(regression.clf_ is None)
    self.assertEqual(regression.fitted_, False)
    regression.partial_fit(X, y)
    self.assertTrue(regression.clf_ is not None)
    self.assertEqual(regression.fitted_, True)

  @requireEmbedded
  def test_predict(self):
    X = np.array([[1,1], [0,0]])
    y = np.array([1,2])
    regression = LinearRegression()
    self.assertRaises(RuntimeError, regression.predict, X)
    regression.fit(X, y)
    y_pred = regression.predict(X)
    self.assertEqual(y_pred.shape[0], X.shape[0])
 
  @requireEmbedded
  def test_class_params(self):
    regression = LinearRegression()
    params = ['method', 'regularization_weight', 'sensitivity', 'learning_rate',
              'n_iter', 'shuffle', 'embedded', 'seed']
    for param in params:
      self.assertTrue(param in regression.__dict__)
    self.assertTrue('invalid_param' not in regression.__dict__)

  @requireEmbedded
  def test_get_params(self):
    params = {
      'method': 'CW',
      'regularization_weight': 5.0,
      'sensitivity': 1.0,
      'learning_rate': 0.1,
      'n_iter': 5,
      'shuffle': True,
      'embedded': True,
      'seed': 42
    }
    regression = LinearRegression(**params)
    self.assertDictEqual(params, regression.get_params())
    regression.stop()

  @requireEmbedded
  def test_set_params(self):
    params = {
      'method': 'CW',
      'regularization_weight': 5.0,
      'sensitivity': 1.0,
      'learning_rate': 0.1,
      'n_iter': 5,
      'shuffle': True,
      'embedded': True,
      'seed': 42
    }
    regression = LinearRegression()
    regression.set_params(**params)
    self.assertEqual(regression.method, params['method'])
    self.assertEqual(regression.regularization_weight, params['regularization_weight'])
    self.assertEqual(regression.sensitivity, params['sensitivity'])
    self.assertEqual(regression.learning_rate, params['learning_rate'])
    self.assertEqual(regression.n_iter, params['n_iter'])
    self.assertEqual(regression.shuffle, params['shuffle'])
    self.assertEqual(regression.embedded, params['embedded'])
    self.assertEqual(regression.seed, params['seed'])

  @requireEmbedded
  def test_save(self):
    name = 'test'
    regression = LinearRegression()
    regression.save(name)


class NearestNeighborsRegressionTest(TestCase):

  def test_simple(self):
    regression = NearestNeighborsRegression()
    regression.stop()

  @requireEmbedded
  def test_embedded(self):
    regression = NearestNeighborsRegression(embedded=True)

  @requireEmbedded
  def test_launch_regression(self):
    methods = ['euclid_lsh', 'lsh', 'minhash', 'euclidean', 'cosine']
    def launch_regression(method):
      regression = NearestNeighborsRegression(method=method)
      regression._launch_regression()
    for method in methods:
      self.assertEqual(launch_regression(method), None)
    self.assertRaises(NotImplementedError, launch_regression, 'inverted_index')

  @requireEmbedded
  def test_partial_fit(self):
    X = np.array([[1,1], [0,0]])
    y = np.array([1,2])
    regression = NearestNeighborsRegression()
    self.assertTrue(regression.clf_ is None)
    self.assertEqual(regression.fitted_, False)
    regression.partial_fit(X, y)
    self.assertTrue(regression.clf_ is not None)
    self.assertEqual(regression.fitted_, True)
    regression.stop()

  @requireEmbedded
  def test_predict(self):
    X = np.array([[1,1], [0,0]])
    y = np.array([1,2])
    regression = NearestNeighborsRegression()
    self.assertRaises(RuntimeError, regression.predict, X)
    regression.fit(X, y)
    y_pred = regression.predict(X)
    self.assertEqual(y_pred.shape[0], X.shape[0])

  @requireEmbedded
  def test_class_params(self):
    regression = NearestNeighborsRegression()
    params = ['method', 'nearest_neighbor_num',
            'hash_num', 'n_iter', 'shuffle', 'embedded', 'seed']
    for param in params:
      self.assertTrue(param in regression.__dict__)
    self.assertTrue('invalid_param' not in regression.__dict__)

  @requireEmbedded
  def test_get_params(self):
    params = {
      'method': 'lsh',
      'nearest_neighbor_num': 10,
      'hash_num': 512,
      'n_iter': 5,
      'shuffle': True,
      'embedded': True,
      'seed': 42
    }
    regression = NearestNeighborsRegression(**params)
    self.assertDictEqual(params, regression.get_params())

  @requireEmbedded
  def test_set_params(self):
    params = {
      'method': 'lsh',
      'nearest_neighbor_num': 10,
      'hash_num': 512,
      'n_iter': 5,
      'shuffle': True,
      'embedded': True,
      'seed': 42
    }
    regression = NearestNeighborsRegression()
    regression.set_params(**params)
    self.assertEqual(regression.method, params['method'])
    self.assertEqual(regression.nearest_neighbor_num, params['nearest_neighbor_num'])
    self.assertEqual(regression.hash_num, params['hash_num'])
    self.assertEqual(regression.n_iter, params['n_iter'])
    self.assertEqual(regression.shuffle, params['shuffle'])
    self.assertEqual(regression.embedded, params['embedded'])
    self.assertEqual(regression.seed, params['seed'])

  @requireEmbedded
  def test_save(self):
    name = 'test'
    regression = NearestNeighborsRegression()
    regression.save(name)


