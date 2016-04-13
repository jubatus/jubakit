# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.base import BaseLoader, BaseSchema, BaseDataset, BaseService, BaseConfig, GenericConfig

from .stub import *

class BaseSchemaTest(TestCase):
  def test_simple(self):
    schema = BaseSchema({
      'k1': BaseSchema.STRING,
      'k2': BaseSchema.NUMBER,
      'k3': BaseSchema.BINARY,
    })
    d = schema.transform({
      'k1': '123',
      'k2': 456,
      'k3': chr(0),
    })

    self.assertEqual({'k1': '123'}, dict(d.string_values))
    self.assertEqual({'k2': 456}, dict(d.num_values))
    self.assertEqual({'k3': chr(0)}, dict(d.binary_values))

  def test_alias(self):
    schema = BaseSchema({
      'k1': BaseSchema.NUMBER,
      'k2': (BaseSchema.NUMBER, 'alias_name'),
    })
    d = schema.transform({
      'k1': '123',
      'k2': 456,
    })

    self.assertEqual({'k1': 123, 'alias_name': 456}, dict(d.num_values))

  def test_fallback(self):
    schema = BaseSchema({
      'k1': BaseSchema.STRING,
    }, BaseSchema.NUMBER)
    d = schema.transform({
      'k1': '123',
      'k2': 456,
      'k3': 789,
    })

    self.assertEqual({'k1': '123'}, dict(d.string_values))
    self.assertEqual({'k2': 456, 'k3': 789}, dict(d.num_values))

  def test_unknown_key_name(self):
    schema = BaseSchema({
      'k1': BaseSchema.STRING,
      'k2': BaseSchema.NUMBER,
    })
    self.assertRaises(RuntimeError, schema.transform, {
      'k1': '123',
      'k2': 456,
      'k3': 789,
    })

  def test_predict(self):
    row = {'num1': 10, 'num2': 10.0, 'num3': 'inf', 'str1': 'abc', 'str2': '0.0.1'}
    schema = BaseSchema.predict(row)
    d = schema.transform(row)

    self.assertEqual({'str1': 'abc', 'str2': '0.0.1'}, dict(d.string_values))
    self.assertEqual({'num1': 10, 'num2': 10.0, 'num3': float('inf')}, dict(d.num_values))

class BaseDatasetTest(TestCase):
  SCHEMA = BaseSchema({
    'value': BaseSchema.NUMBER,
  })

  def test_static(self):
    loader = StubLoader()
    ds = BaseDataset(loader, self.SCHEMA)

    self.assertTrue(ds.is_static())
    self.assertEqual(3, len(ds))
    self.assertEqual({'value': 1}, dict(ds[0].num_values))
    self.assertEqual({'value': 2}, dict(ds[1].num_values))
    self.assertEqual({'value': 3}, dict(ds[2].num_values))

    ds2 = ds[(1,2)]
    self.assertEqual(2, len(ds2))
    self.assertEqual({'value': 2}, dict(ds2[0].num_values))
    self.assertEqual({'value': 3}, dict(ds2[1].num_values))

    expected_idx = 0
    for (idx, row) in ds:
      self.assertEqual(expected_idx, idx)
      self.assertEqual({'value': idx+1}, dict(row.num_values))
      expected_idx += 1

  def test_shuffle(self):
    loader = StubLoader()
    ds = BaseDataset(loader, self.SCHEMA).shuffle()

    rows = []
    for (_, row) in ds:
      rows.append(row)

    row_values = [x.num_values[0][1] for x in rows]
    self.assertEqual([1,2,3], sorted(row_values))

  def test_nonstatic(self):
    loader = StubLoader()
    ds = BaseDataset(loader, self.SCHEMA, False)
    self.assertFalse(ds.is_static())

    expected_idx = 0
    for (idx, row) in ds:
      self.assertEqual(expected_idx, idx)
      self.assertEqual({'value': idx+1}, dict(row.num_values))
      expected_idx += 1

  def test_infinite(self):
    loader = StubInfiniteLoader()
    ds = BaseDataset(loader, self.SCHEMA)
    self.assertFalse(ds.is_static())

    expected_idx = 0
    for (idx, row) in ds:
      self.assertEqual(expected_idx, idx)
      self.assertEqual({'value': idx+1}, dict(row.num_values))
      expected_idx += 1
      if 10 < expected_idx:
        break

class TestBaseService(TestCase):
  def test_simple(self):
    service = StubService()

class TestBaseConfig(TestCase):
  def test_simple(self):
    config = StubConfig()
    self.assertEqual({'test': 1.0}, config)

class TestGenericConfg(TestCase):
  def test_simple(self):
    config = StubGenericConfig()
    self.assertEqual('test', config['method'])

  def test_clear_converter(self):
    config = StubGenericConfig()
    self.assertTrue('unigram' in config['converter']['string_types'])
    config.clear_converter()
    self.assertFalse('unigram' in config['converter']['string_types'])

  def test_add_mecab(self):
    config = StubGenericConfig()
    self.assertFalse('mecab2' in config['converter']['string_types'])
    config.add_mecab(name='mecab2', ngram=2)
    self.assertTrue('mecab2' in config['converter']['string_types'])
    self.assertEqual('2', config['converter']['string_types']['mecab2']['ngram'])
