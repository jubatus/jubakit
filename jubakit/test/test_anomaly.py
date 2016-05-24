# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.anomaly import Schema, Dataset, Anomaly, Config
from jubakit.compat import *

from .stub import *

class SchemaTest(TestCase):
  def test_simple(self):
    schema = Schema({
      'id': Schema.ID,
      'k1': Schema.STRING,
      'k2': Schema.NUMBER,
      'f':  Schema.FLAG,
    })
    (row_id, flag, d) = schema.transform({'id': 'user001', 'k1': 'abc', 'k2': '123', 'f': 'True'})

    self.assertEqual(row_id, 'user001')
    self.assertEqual(flag, 'True')
    self.assertEqual({'k1': 'abc'}, dict(d.string_values))
    self.assertEqual({'k2': 123}, dict(d.num_values))

  def test_illegal_label(self):
    # schema with multiple IDs
    self.assertRaises(RuntimeError, Schema, {
      'k1': Schema.ID,
      'k2': Schema.ID,
    })

    # schema fallback set to FLAG
    self.assertRaises(RuntimeError, Schema, {
      'k1': Schema.ID
    }, Schema.FLAG)

    # schema fallback set to ID
    self.assertRaises(RuntimeError, Schema, {
      'k1': Schema.FLAG
    }, Schema.ID)

class DatasetTest(TestCase):
  def test_predict(self):
    loader = StubLoader()
    dataset = Dataset(loader, None)  # predict
    self.assertEqual(['v', 1.0], dataset[0][2].num_values[0])

class AnomalyTest(TestCase):
  def test_simple(self):
    anomaly = Anomaly()

class ConfigTest(TestCase):
  def test_simple(self):
    config = Config()
    self.assertEqual('lof', config['method'])

  def test_methods(self):
    config = Config()
    self.assertTrue(isinstance(config.methods(), list))

  def test_default(self):
    config = Config.default()
    self.assertEqual('lof', config['method'])

  def test_method_param(self):
    self.assertTrue(Config(method='lof')['parameter']['ignore_kth_same_point'])
    self.assertEquals('inverted_index_euclid', Config(method='lof')['parameter']['method'])
    self.assertEquals('euclid_lsh', Config(method='light_lof')['parameter']['method'])
