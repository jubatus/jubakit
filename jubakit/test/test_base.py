# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.base import BaseLoader, BaseSchema, GenericSchema, BaseDataset, BaseService, BaseConfig, GenericConfig

from .stub import *

class BaseLoaderTest(TestCase):
  def test_simple(self):
    loader = BaseLoader()
    self.assertFalse(loader.is_infinite())

class BaseSchemaTest(TestCase):
  def test_simple(self):
    schema = BaseSchema({
      'k1': BaseSchema.IGNORE,
      'k2': BaseSchema.AUTO,
      'k3': (BaseSchema.INFER, 'ailas_k3'),
    })
    self.assertRaises(NotImplementedError, schema.transform, {})
    self.assertRaises(NotImplementedError, schema.predict, {}, True)

class GenericSchemaTest(TestCase):
  def test_simple(self):
    schema = GenericSchema({
      'k1': GenericSchema.STRING,
      'k2': GenericSchema.NUMBER,
      'k3': GenericSchema.BINARY,
    })
    d = schema.transform({
      'k1': '123',
      'k2': 456,
      'k3': 'xxx'.encode(),
    })

    self.assertEqual({'k1': '123'}, dict(d.string_values))
    self.assertEqual({'k2': 456}, dict(d.num_values))
    self.assertEqual({'k3': 'xxx'.encode()}, dict(d.binary_values))

  def test_alias(self):
    schema = GenericSchema({
      'k1': GenericSchema.NUMBER,
      'k2': (GenericSchema.NUMBER, 'alias_name'),
    })
    d = schema.transform({
      'k1': '123',
      'k2': 456,
    })

    self.assertEqual({'k1': 123, 'alias_name': 456}, dict(d.num_values))

  def test_fallback(self):
    schema = GenericSchema({
      'k1': GenericSchema.STRING,
    }, GenericSchema.NUMBER)
    d = schema.transform({
      'k1': '123',
      'k2': 456,
      'k3': 789,
    })

    self.assertEqual({'k1': '123'}, dict(d.string_values))
    self.assertEqual({'k2': 456, 'k3': 789}, dict(d.num_values))

  def test_unknown_key_name(self):
    schema = GenericSchema({
      'k1': GenericSchema.STRING,
      'k2': GenericSchema.NUMBER,
    })

    self.assertRaises(RuntimeError, schema.transform, {
      'k1': '123',
      'k2': 456,
      'k3': 789,
    })

  def test_auto(self):
    schema = GenericSchema({
      'k1': GenericSchema.AUTO,
      'k2': GenericSchema.AUTO,
      'k3': GenericSchema.AUTO,
      'k4': GenericSchema.AUTO,
    })
    d = schema.transform({
      'k1': '123',
      'k2': 456,
      'k3': '789'.encode(),
      'k4': 'xxx'.encode(),
    })

    self.assertEqual({'k1': '123'}, dict(d.string_values))
    self.assertEqual({'k2': 456}, dict(d.num_values))
    self.assertEqual({'k3': '789'.encode(), 'k4': 'xxx'.encode()}, dict(d.binary_values))

  def test_infer(self):
    schema = GenericSchema({
      'k1': GenericSchema.INFER,
      'k2': GenericSchema.INFER,
      'k3': GenericSchema.INFER,
      'k4': GenericSchema.INFER,
    })
    d = schema.transform({
      'k1': '123',
      'k2': 456,
      'k3': '789'.encode(),
      'k4': 'xxx'.encode(),
    })

    self.assertEqual({'k4': 'xxx'}, dict(d.string_values))
    self.assertEqual({'k1': 123, 'k2': 456, 'k3': 789}, dict(d.num_values))
    self.assertEqual({}, dict(d.binary_values))

  def test_ignore(self):
    schema = GenericSchema({
      'k1': GenericSchema.NUMBER,
    }, GenericSchema.IGNORE)
    d = schema.transform({
      'k1': '123',
      'k2': 456,
    })

    self.assertEqual({}, dict(d.string_values))
    self.assertEqual({'k1': 123}, dict(d.num_values))
    self.assertEqual({}, dict(d.binary_values))

  def test_predict(self):
    row = {'num1': 10, 'num2': 10.0, 'num3': 'inf', 'str1': 'abc', 'str2': '0.0.1'}
    schema = GenericSchema.predict(row, False)
    d = schema.transform(row)

    self.assertEqual({'str1': 'abc', 'str2': '0.0.1'}, dict(d.string_values))
    self.assertEqual({'num1': 10, 'num2': 10.0, 'num3': float('inf')}, dict(d.num_values))

  def test_predict_typed(self):
    row = {'num1': 10, 'num2': 10.0, 'num3': 'inf', 'str1': 'abc', 'str2': '0.0.1'}
    schema = GenericSchema.predict(row, True)
    d = schema.transform(row)

    self.assertEqual({'str1': 'abc', 'str2': '0.0.1', 'num3': 'inf'}, dict(d.string_values))
    self.assertEqual({'num1': 10, 'num2': 10.0}, dict(d.num_values))

  def test_invalid(self):
    schema = GenericSchema({'k1': 'unknown'})
    self.assertRaises(RuntimeError, schema.transform, {'k1': '123'})

class BaseDatasetTest(TestCase):
  SCHEMA = GenericSchema({
    'v': (GenericSchema.NUMBER, 'value'),
  })

  def test_static(self):
    loader = StubLoader()
    ds = BaseDataset(loader, self.SCHEMA)

    self.assertTrue(ds.is_static())
    self.assertEqual(3, len(ds))
    self.assertEqual({'value': 1}, dict(ds[0].num_values))
    self.assertEqual({'value': 2}, dict(ds[1].num_values))
    self.assertEqual({'value': 3}, dict(ds[2].num_values))
    self.assertEqual({'v': 1}, dict(ds.get(0)))
    self.assertEqual({'v': 2}, dict(ds.get(1)))
    self.assertEqual({'v': 3}, dict(ds.get(2)))

    ds2 = ds[(1,2)]
    self.assertEqual(2, len(ds2))
    self.assertEqual({'value': 2}, dict(ds2[0].num_values))
    self.assertEqual({'value': 3}, dict(ds2[1].num_values))
    self.assertEqual({'v': 2}, dict(ds2.get(0)))
    self.assertEqual({'v': 3}, dict(ds2.get(1)))

    expected_idx = 0
    for (idx, row) in ds:
      self.assertEqual(expected_idx, idx)
      self.assertEqual({'value': idx+1}, dict(row.num_values))
      expected_idx += 1

  def test_get_schema(self):
    loader = StubLoader()
    ds = BaseDataset(loader, self.SCHEMA)
    self.assertEqual(self.SCHEMA, ds.get_schema())

  def test_shuffle(self):
    loader = StubLoader()
    ds = BaseDataset(loader, self.SCHEMA).shuffle(0)

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
      self.assertEqual(row.num_values, ds[idx].num_values)
      self.assertEqual({'v': idx+1}, ds.get(idx))
      expected_idx += 1

  def test_nonstatic_ops(self):
    loader = StubLoader()
    ds = BaseDataset(loader, self.SCHEMA, False)

    self.assertRaises(RuntimeError, ds.convert, lambda x:x)
    self.assertRaises(RuntimeError, ds.get, 0)
    self.assertRaises(RuntimeError, len, ds)
    self.assertRaises(RuntimeError, lambda: ds[0])

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
    self.assertTrue('parameter' not in config)

  def test_param(self):
    config = StubGenericConfig(method='test2')
    self.assertEqual('test2', config['method'])
    self.assertEqual(1, config['parameter']['param1'])
    self.assertEqual(2, config['parameter']['param2'])

  def test_param_append(self):
    config = StubGenericConfig(method='test', parameter={'param0': 0})
    self.assertEqual('test', config['method'])
    self.assertEqual(0, config['parameter']['param0'])

  def test_param_overwrite(self):
    config = StubGenericConfig(method='test2', parameter={'param2': 1}, converter={'string_types': []})
    self.assertEqual('test2', config['method'])
    self.assertEqual(1, config['parameter']['param1'])
    self.assertEqual(1, config['parameter']['param2'])
    self.assertTrue('string_rules' in config['converter'])
    self.assertEqual(0, len(config['converter']['string_types']))

  def test_clear_converter(self):
    config = StubGenericConfig()
    self.assertTrue('unigram' in config['converter']['string_types'])
    config.clear_converter()
    self.assertFalse('unigram' in config['converter']['string_types'])

  def test_add_mecab(self):
    config = StubGenericConfig()
    self.assertFalse('mecab2' in config['converter']['string_types'])
    config.add_mecab(name='mecab2', ngram=2, base=True)
    self.assertTrue('mecab2' in config['converter']['string_types'])
    self.assertEqual('2', config['converter']['string_types']['mecab2']['ngram'])
    self.assertEqual('true', config['converter']['string_types']['mecab2']['base'])
