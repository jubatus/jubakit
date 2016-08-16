# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.recommender import Schema, Dataset, Recommender, Config
from jubakit.compat import *

from .stub import *

class SchemaTest(TestCase):
  def test_simple(self):
    schema = Schema({
      'id': Schema.ID,
      'k1': Schema.STRING,
      'k2': Schema.NUMBER,
    })
    (row_id, d) = schema.transform({'id': 'user001', 'k1': 'abc', 'k2': '123'})

    self.assertEqual(row_id, 'user001')
    self.assertEqual({'k1': 'abc'}, dict(d.string_values))
    self.assertEqual({'k2': 123}, dict(d.num_values))

  def test_illegal_label(self):
    # schema with multiple IDs
    self.assertRaises(RuntimeError, Schema, {
      'k1': Schema.ID,
      'k2': Schema.ID,
    })

class DatasetTest(TestCase):
  def test_predict(self):
    loader = StubLoader()
    dataset = Dataset(loader, None)  # predict
    self.assertEqual(['v', 1.0], dataset[0][1].num_values[0])

class RecommenderTest(TestCase):
  def test_simple(self):
    recommender = Recommender()

class ConfigTest(TestCase):
  def test_simple(self):
    config = Config()
    self.assertEqual('lsh', config['method'])

  def test_methods(self):
    config = Config()
    self.assertTrue(isinstance(config.methods(), list))

  def test_default(self):
    config = Config.default()
    self.assertEqual('lsh', config['method'])

  def test_method_param(self):
    self.assertTrue('parameter' not in Config(method='inverted_index'))
    self.assertTrue('hash_num' in Config(method='minhash')['parameter']) 
    self.assertTrue('hash_num' in Config(method='lsh')['parameter']) 
    self.assertTrue('threads' in Config(method='lsh')['parameter']) 
    self.assertTrue('method' in Config(method='nearest_neighbor_recommender')['parameter'])    
    self.assertTrue('parameter' in Config(method='nearest_neighbor_recommender')['parameter'])    
    self.assertTrue('threads' in 
            Config(method='nearest_neighbor_recommender')['parameter']['parameter'])
    self.assertTrue('hash_num' in 
            Config(method='nearest_neighbor_recommender')['parameter']['parameter'])

  def test_invalid_method(self):
    self.assertRaises(RuntimeError, Config._default_parameter, 'invalid_method')
