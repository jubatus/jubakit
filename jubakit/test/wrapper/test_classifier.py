# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

try:
  import numpy as np
except ImportError:
  pass

from jubakit.wrapper.classifier import LinearClassifier, NearestNeighborsClassifier
from . import requireEmbedded


class LinearClassifierTest(TestCase):
  
  def test_simple(self):
    classifier = LinearClassifier()
    classifier.stop()

  @requireEmbedded
  def test_embedded(self):
    classifier = LinearClassifier(embedded=True)

  @requireEmbedded
  def test_launch_classifier(self):
    methods = ['AROW', 'CW', 'NHERD', 'PA', 'PA1', 'PA2', 'perceptron']
    def launch_classifier(method):
      classifier = LinearClassifier(method=method)
      classifier._launch_classifier()
    for method in methods:
      self.assertEqual(launch_classifier(method), None)
    self.assertRaises(NotImplementedError, launch_classifier, 'Logistic Regression')

  @requireEmbedded
  def test_partial_fit(self):
    X = np.array([[1,1], [0,0]])
    y = np.array([1,2])
    classifier = LinearClassifier()
    self.assertTrue(classifier.clf_ is None)
    self.assertEqual(classifier.fitted_, False)
    classifier.partial_fit(X, y)
    self.assertTrue(classifier.clf_ is not None)
    self.assertEqual(classifier.fitted_, True)

  @requireEmbedded
  def test_predict(self):
    X = np.array([[1,1], [0,0]])
    y = np.array([1,2])
    classifier = LinearClassifier()
    self.assertRaises(RuntimeError, classifier.predict, X)
    classifier.fit(X, y)
    y_pred = classifier.predict(X)
    self.assertEqual(y_pred.shape[0], X.shape[0])
  
  @requireEmbedded
  def test_decision_function(self):
    X = np.array([[1,1], [0,0]])
    y = np.array([1,2])
    c = np.unique(y)
    classifier = LinearClassifier()
    self.assertRaises(RuntimeError, classifier.predict, X)
    classifier.fit(X, y)
    y_pred = classifier.decision_function(X)
    self.assertEqual(y_pred.shape, (X.shape[0], c.shape[0]))

  @requireEmbedded
  def test_class_params(self):
    classifier = LinearClassifier()
    params = ['method', 'regularization_weight',
              'softmax', 'n_iter', 'shuffle', 'embedded', 'seed']
    for param in params:
      self.assertTrue(param in classifier.__dict__)
    self.assertTrue('invalid_param' not in classifier.__dict__)

  @requireEmbedded
  def test_get_params(self):
    params = {
      'method': 'CW', 
      'regularization_weight': 5.0,
      'softmax': True,
      'n_iter': 5,
      'shuffle': True,
      'embedded': True,
      'seed': 42
    }
    classifier = LinearClassifier(**params)
    self.assertDictEqual(params, classifier.get_params())
    classifier.stop()

  @requireEmbedded
  def test_set_params(self):
    params = {
      'method': 'CW', 
      'regularization_weight': 5.0,
      'softmax': True,
      'n_iter': 5,
      'shuffle': True,
      'embedded': True,
      'seed': 42
    }
    classifier = LinearClassifier()
    classifier.set_params(**params)
    self.assertEqual(classifier.method, params['method'])
    self.assertEqual(classifier.regularization_weight, params['regularization_weight'])
    self.assertEqual(classifier.softmax, params['softmax'])
    self.assertEqual(classifier.n_iter, params['n_iter'])
    self.assertEqual(classifier.shuffle, params['shuffle'])
    self.assertEqual(classifier.embedded, params['embedded'])
    self.assertEqual(classifier.seed, params['seed'])

  @requireEmbedded
  def test_save(self):
    name = 'test'
    classifier = LinearClassifier()
    classifier.save(name)


class NearestNeighborsClassifierTest(TestCase):
  
  def test_simple(self):
    classifier = NearestNeighborsClassifier()
    classifier.stop()

  @requireEmbedded
  def test_embedded(self):
    classifier = NearestNeighborsClassifier(embedded=True)

  @requireEmbedded
  def test_launch_classifier(self):
    methods = ['euclid_lsh', 'lsh', 'minhash', 'euclidean', 'cosine']
    def launch_classifier(method):
      classifier = NearestNeighborsClassifier(method=method)
      classifier._launch_classifier()
    for method in methods:
      self.assertEqual(launch_classifier(method), None)
    self.assertRaises(NotImplementedError, launch_classifier, 'inverted_index')

  @requireEmbedded
  def test_partial_fit(self):
    X = np.array([[1,1], [0,0]])
    y = np.array([1,2])
    classifier = NearestNeighborsClassifier()
    self.assertTrue(classifier.clf_ is None)
    self.assertEqual(classifier.fitted_, False)
    classifier.partial_fit(X, y)
    self.assertTrue(classifier.clf_ is not None)
    self.assertEqual(classifier.fitted_, True)
    classifier.stop()

  @requireEmbedded
  def test_predict(self):
    X = np.array([[1,1], [0,0]])
    y = np.array([1,2])
    classifier = NearestNeighborsClassifier()
    self.assertRaises(RuntimeError, classifier.predict, X)
    classifier.fit(X, y)
    y_pred = classifier.predict(X)
    self.assertEqual(y_pred.shape[0], X.shape[0])

  @requireEmbedded
  def test_decision_function(self):
    X = np.array([[1,1], [0,0]])
    y = np.array([1,2])
    c = np.unique(y)
    classifier = NearestNeighborsClassifier()
    self.assertRaises(RuntimeError, classifier.predict, X)
    classifier.fit(X, y)
    y_pred = classifier.decision_function(X)
    self.assertEqual(y_pred.shape, (X.shape[0], c.shape[0]))

  @requireEmbedded
  def test_class_params(self):
    classifier = NearestNeighborsClassifier()
    params = ['method', 'nearest_neighbor_num', 'local_sensitivity',
              'hash_num', 'softmax', 'n_iter', 'shuffle', 'embedded', 'seed']
    for param in params:
      self.assertTrue(param in classifier.__dict__)
    self.assertTrue('invalid_param' not in classifier.__dict__)

  @requireEmbedded
  def test_get_params(self):
    params = {
      'method': 'lsh', 
      'nearest_neighbor_num': 10,
      'local_sensitivity': 0.1,
      'hash_num': 512,
      'softmax': True,
      'n_iter': 5,
      'shuffle': True,
      'embedded': True,
      'seed': 42
    }
    classifier = NearestNeighborsClassifier(**params)
    self.assertDictEqual(params, classifier.get_params())

  @requireEmbedded
  def test_set_params(self):
    params = {
      'method': 'lsh', 
      'nearest_neighbor_num': 10,
      'local_sensitivity': 0.1,
      'hash_num': 512,
      'softmax': True,
      'n_iter': 5,
      'shuffle': True,
      'embedded': True,
      'seed': 42
    }
    classifier = NearestNeighborsClassifier()
    classifier.set_params(**params)
    self.assertEqual(classifier.method, params['method'])
    self.assertEqual(classifier.nearest_neighbor_num, params['nearest_neighbor_num'])
    self.assertEqual(classifier.local_sensitivity, params['local_sensitivity'])
    self.assertEqual(classifier.hash_num, params['hash_num'])
    self.assertEqual(classifier.softmax, params['softmax'])
    self.assertEqual(classifier.n_iter, params['n_iter'])
    self.assertEqual(classifier.shuffle, params['shuffle'])
    self.assertEqual(classifier.embedded, params['embedded'])
    self.assertEqual(classifier.seed, params['seed'])
   
  @requireEmbedded
  def test_save(self):
    name = 'test'
    classifier = NearestNeighborsClassifier()
    classifier.save(name)


