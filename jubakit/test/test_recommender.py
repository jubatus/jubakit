# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import warnings

from unittest import TestCase

from jubakit.recommender import Schema, Dataset, Recommender, Config
from jubakit.compat import *

from . import requireEmbedded
from .stub import *

def filter_warning():
  if sys.version_info > (3, 0):
    warnings.simplefilter("ignore", ResourceWarning)

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

  def test_illegal_id(self):
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

  @requireEmbedded
  def test_embedded(self):
    recommender = Recommender.run(Config(), embedded=True)

  def test_clear_row(self):
    recommender = Recommender.run(Config())
    loader = StubLoader()

    # dataset must have id when execute `clear_row`.
    schema = Schema({'v': Schema.NUMBER})
    dataset = Dataset(loader, schema)
    def func():
      for _ in recommender.clear_row(dataset): pass
    self.assertRaises(RuntimeError, lambda: func())

    schema = Schema({'v': Schema.ID})
    dataset = Dataset(loader, schema)

    # expect to get False when table is empty.
    for (idx, row_id, result) in recommender.clear_row(dataset):
      self.assertEqual(result, True)

    recommender.stop()

  def test_update_row(self):
    recommender = Recommender.run(Config())
    loader = StubLoader()

    # dataset must have id when execute `update_row`
    schema = Schema({'v': Schema.NUMBER})
    dataset = Dataset(loader, schema)
    def func():
      for _ in recommender.update_row(dataset): pass
    self.assertRaises(RuntimeError, lambda: func())

    schema = Schema({'v': Schema.ID})
    dataset = Dataset(loader, schema)
    for (idx, row_id, result) in recommender.update_row(dataset):
      self.assertEqual(result, True)
    recommender.stop()

  def test_complete_row_from_id(self):
    filter_warning()
    recommender = Recommender.run(Config())
    loader = StubLoader()

    # dataset must have id when execute `complete_row_from_id`
    schema = Schema({'v': Schema.NUMBER})
    dataset = Dataset(loader, schema)
    def func():
      for _ in recommender.complete_row_from_id(dataset): pass
    self.assertRaises(RuntimeError, lambda: func())

    schema = Schema({'v': Schema.ID})
    dataset = Dataset(loader, schema)
    for (idx, row_id, d) in recommender.complete_row_from_id(dataset):
      self.assertEqual(0, len(d.string_values))
      self.assertEqual(0, len(d.num_values))
      self.assertEqual(0, len(d.binary_values))

    recommender.stop()

  def test_complete_row_from_datum(self):
    filter_warning()
    recommender = Recommender.run(Config())
    loader = StubLoader()

    schema = Schema({'v': Schema.ID})
    dataset = Dataset(loader, schema)
    for (idx, row_id, d) in recommender.complete_row_from_datum(dataset):
      self.assertEqual(0, len(d.string_values))
      self.assertEqual(0, len(d.num_values))
      self.assertEqual(0, len(d.binary_values))

    schema = Schema({'v': Schema.NUMBER})
    dataset = Dataset(loader, schema)
    for (idx, row_id, d) in recommender.complete_row_from_datum(dataset):
      self.assertEqual(None, row_id)    # there is no id in column_table.
      self.assertEqual(0, len(d.string_values))
      self.assertEqual(0, len(d.num_values))
      self.assertEqual(0, len(d.binary_values))

    recommender.stop()

  def test_similar_row_from_id(self):
    filter_warning()
    recommender = Recommender.run(Config())
    loader = StubLoader()

    # dataset must have id when execute `similar_row_from_id`
    schema = Schema({'v': Schema.NUMBER})
    dataset = Dataset(loader, schema)
    def func():
      for _ in recommender.similar_row_from_id(dataset): pass
    self.assertRaises(RuntimeError, lambda: func())

    schema = Schema({'v': Schema.ID})
    dataset = Dataset(loader, schema)
    for (idx, row_id, d) in recommender.complete_row_from_id(dataset):
      self.assertEqual(0, len(d.string_values))
      self.assertEqual(0, len(d.num_values))
      self.assertEqual(0, len(d.binary_values))

    recommender.stop()

  def test_similar_row_from_id_and_score(self):
    filter_warning()
    recommender = Recommender.run(Config())
    loader = StubLoader()

    # dataset must have id when execute `similar_row_from_id_and_score`
    schema = Schema({'v': Schema.NUMBER})
    dataset = Dataset(loader, schema)
    def func():
      for _ in recommender.similar_row_from_id_and_score(dataset): pass
    self.assertRaises(RuntimeError, lambda: func())

    schema = Schema({'v': Schema.ID})
    dataset = Dataset(loader, schema)
    for (idx, row_id, result) in recommender.similar_row_from_id_and_score(dataset):
      self.assertEqual(str(idx+1), row_id)    # there is no id in column_table
      self.assertEqual(0, len(result))  # there is no similar row in column_table

    recommender.stop()

  def test_similar_row_from_id_and_rate(self):
    filter_warning()
    recommender = Recommender.run(Config())
    loader = StubLoader()

    # dataset must have id when execute `similar_row_from_id_and_rate`
    schema = Schema({'v': Schema.NUMBER})
    dataset = Dataset(loader, schema)
    def func():
      for _ in recommender.similar_row_from_id_and_rate(dataset): pass
    self.assertRaises(RuntimeError, lambda: func())

    # rate must be in (0, 1].
    def func():
      for _ in recommender.similar_row_from_id_and_rate(dataset, rate=0.0): pass
    self.assertRaises(ValueError, lambda: func())

    def func():
      for _ in recommender.similar_row_from_id_and_rate(dataset, rate=1.01): pass
    self.assertRaises(ValueError, lambda: func())

    schema = Schema({'v': Schema.ID})
    dataset = Dataset(loader, schema)
    for (idx, row_id, result) in recommender.similar_row_from_id_and_rate(dataset, 1.0):
      self.assertEqual(str(idx+1), row_id)    # there is no id in column_table
      self.assertEqual(0, len(result))  # there is no similar row in column_table

    recommender.stop()

  def test_similar_row_from_datum(self):
    filter_warning()
    recommender = Recommender.run(Config())
    loader = StubLoader()
    schema = Schema({'v': Schema.ID})
    dataset = Dataset(loader, schema)
    for (idx, row_id, result) in recommender.similar_row_from_datum(dataset):
      self.assertEqual(0, len(result))

    schema = Schema({'v': Schema.NUMBER})
    dataset = Dataset(loader, schema)
    for (idx, row_id, result) in recommender.similar_row_from_datum(dataset):
      self.assertEqual(None, row_id)    # there is no id in column_table
      self.assertEqual(0, len(result))  # there is no similar row in column_table

    recommender.stop()

  def test_similar_row_from_datum_and_score(self):
    filter_warning()
    recommender = Recommender.run(Config())
    loader = StubLoader()
    schema = Schema({'v': Schema.ID})
    dataset = Dataset(loader, schema)
    for (idx, row_id, result) in recommender.similar_row_from_datum_and_score(dataset):
      self.assertEqual(0, len(result))

    schema = Schema({'v': Schema.NUMBER})
    dataset = Dataset(loader, schema)
    for (idx, row_id, result) in recommender.similar_row_from_datum_and_score(dataset):
      self.assertEqual(None, row_id)    # there is no id in column_table
      self.assertEqual(0, len(result))  # there is no similar row in column_table

    recommender.stop()

  def test_similar_row_from_datum_and_rate(self):
    filter_warning()
    recommender = Recommender.run(Config())
    loader = StubLoader()
    schema = Schema({'v': Schema.ID})
    dataset = Dataset(loader, schema)
    for (idx, row_id, result) in recommender.similar_row_from_datum_and_rate(dataset):
      self.assertEqual(0, len(result))

    # rate must be in (0, 1].
    def func():
      for _ in recommender.similar_row_from_datum_and_rate(dataset, rate=0.0): pass
    self.assertRaises(ValueError, lambda: func())

    def func():
      for _ in recommender.similar_row_from_datum_and_rate(dataset, rate=1.01): pass
    self.assertRaises(ValueError, lambda: func())

    schema = Schema({'v': Schema.NUMBER})
    dataset = Dataset(loader, schema)
    for (idx, row_id, result) in recommender.similar_row_from_datum_and_rate(dataset):
      self.assertEqual(None, row_id)    # there is no id in column_table
      self.assertEqual(0, len(result))  # there is no similar row in column_table

    recommender.stop()

  def test_decode_row(self):
    filter_warning()
    recommender = Recommender.run(Config())
    loader = StubLoader()

    # dataset must have id when execute `decode_row`
    schema = Schema({'v': Schema.NUMBER})
    dataset = Dataset(loader, schema)
    def func():
      for _ in recommender.decode_row(dataset): pass
    self.assertRaises(RuntimeError, lambda: func())

    schema = Schema({'v': Schema.ID})
    dataset = Dataset(loader, schema)
    for (idx, row_id, d) in recommender.decode_row(dataset):
      self.assertEqual(0, len(d.string_values))
      self.assertEqual(0, len(d.num_values))
      self.assertEqual(0, len(d.binary_values))

    recommender.stop()

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
