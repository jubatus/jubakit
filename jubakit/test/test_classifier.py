# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

import numpy as np
from scipy.sparse import csr_matrix

from jubakit.classifier import Schema, Dataset, Classifier, Config

from .stub import *

class SchemaTest(TestCase):
  def test_simple(self):
    schema = Schema({
      'k1': Schema.STRING,
      'k2': Schema.LABEL,
    })
    (label, d) = schema.transform({'k1': 'abc', 'k2': 'def'})

    self.assertEqual(label, 'def')
    self.assertEqual({'k1': 'abc'}, dict(d.string_values))

  def test_illegal_label(self):
    # schema without label
    self.assertRaises(RuntimeError, Schema, {
      'k1': Schema.STRING,
    })

    # schema with multiple labels
    self.assertRaises(RuntimeError, Schema, {
      'k1': Schema.LABEL,
      'k2': Schema.LABEL
    })

    # schema fallback set to label
    self.assertRaises(RuntimeError, Schema, {
      'k1': Schema.LABEL
    }, Schema.LABEL)

class DatasetTest(TestCase):
  def test_simple(self):
    loader = StubLoader()
    schema = Schema({'value': Schema.LABEL})
    ds = Dataset(loader, schema)
    for (idx, (label, d)) in ds:
      self.assertEqual(idx+1, label)
      self.assertEqual(0, len(d.string_values))
      self.assertEqual(0, len(d.num_values))
      self.assertEqual(0, len(d.binary_values))
    self.assertEqual([1,2,3], list(ds.get_labels()))

  def test_from_array(self):
    ds = Dataset.from_array(
        [ [10,20,30], [20,10,50], [40,10,30] ], # data
        [ 0,          1,          0          ], # labels
        ['k1', 'k2', 'k3'],                     # feature_names
        ['pos', 'neg'],                         # label_names
    )

    expected_labels = ['pos', 'neg', 'pos']
    expected_k1s = [10, 20, 40]
    actual_labels = []
    actual_k1s = []
    for (idx, (label, d)) in ds:
      actual_labels.append(label)
      actual_k1s.append(dict(d.num_values)['k1'])

    self.assertEqual(expected_labels, actual_labels)
    self.assertEqual(expected_k1s, actual_k1s)

  def test_from_matrix(self):
    ds = Dataset.from_matrix(
      self._create_matrix(),    # data
      [ 0, 1, 0 ],              # labels
      [ 'k1', 'k2', 'k3'],      # feature_names
      [ 'pos', 'neg'],          # label_names
    )

    expected_labels = ['pos', 'neg', 'pos']
    expected_k1s = [1,None,4]
    expected_k3s = [2,3,6]
    actual_labels = []
    actual_k1s = []
    actual_k3s = []
    for (idx, (label, d)) in ds:
      actual_labels.append(label)
      actual_k1s.append(dict(d.num_values).get('k1', None))
      actual_k3s.append(dict(d.num_values).get('k3', None))

    self.assertEqual(expected_labels, actual_labels)
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

class ClassifierTest(TestCase):
  def test_simple(self):
    classifier = Classifier()

class ConfigTest(TestCase):
  def test_simple(self):
    config = Config()
    self.assertEqual('AROW', config['method'])

  def test_default(self):
    config = Config.default()
    self.assertEqual('AROW', config['method'])
