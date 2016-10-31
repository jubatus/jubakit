# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

import math

try:
  import numpy as np
except ImportError:
  pass

from jubatus.common import Datum

from jubakit.base import BaseLoader, BaseSchema, GenericSchema, BaseDataset, BaseService, BaseConfig, GenericConfig, Utils

from . import requireSklearn
from .stub import *

class BaseLoaderTest(TestCase):
  def test_base(self):
    loader = BaseLoader()
    self.assertFalse(loader.is_infinite())
    self.assertRaises(NotImplementedError, loader.rows)

  def test_simple(self):
    loader = StubLoader()
    # None should not appear.
    self.assertEqual([{'v': 1}, {'v': 2}, {'v': 3}], list(loader))

class BaseSchemaTest(TestCase):
  def test_base(self):
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

  def test_empty(self):
    schema = GenericSchema({
      'k1': GenericSchema.STRING,
      'k2': GenericSchema.NUMBER,
      'k3': GenericSchema.NUMBER,
    })
    d = schema.transform({
      'k1': '',
      'k2': '',
      'k3': b'',
    })

    self.assertEqual({'k1': ''}, dict(d.string_values))
    self.assertEqual({}, dict(d.num_values))

  @requireSklearn
  def test_numpy(self):
    schema = GenericSchema({
      'k1': GenericSchema.STRING,
      'k2': GenericSchema.NUMBER,
    })
    d = schema.transform({
      'k1': np.float64(1.0),
      'k2': np.float64(1.0),
    })

    self.assertEqual({'k1': '1.0'}, dict(d.string_values))
    self.assertEqual({'k2': 1.0}, dict(d.num_values))

  def test_null(self):
    schema = GenericSchema({
      'k1': GenericSchema.STRING,
      'k2': GenericSchema.NUMBER,
    })
    d = schema.transform({
      'k1': None,
      'k2': None,
    })

    self.assertEqual({}, dict(d.string_values))
    self.assertEqual({}, dict(d.num_values))

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

  def test_string(self):
    schema = GenericSchema({}, GenericSchema.STRING)
    d = schema.transform({
      'k1': '123'.encode(),  # bytes
      'k2': '456',  # unicode
      'k3': 789,  # int
      'k4': 789.0,  # float
      'k5': True,  # bool
      'k6': False,  # bool
    })
    self.assertEqual({
      'k1': '123',
      'k2': '456',
      'k3': '789',
      'k4': '789.0',
      'k5': '1',
      'k6': '0',
    }, dict(d.string_values))
    self.assertEqual({}, dict(d.num_values))
    self.assertEqual({}, dict(d.binary_values))

  def test_number(self):
    schema = GenericSchema({}, GenericSchema.NUMBER)
    d = schema.transform({
      'k1': '123'.encode(),  # bytes
      'k2': '456',  # unicode
      'k3': 789,  # int
      'k4': 789.0,  # float
      'k5': True,  # bool
      'k6': False,  # bool
    })
    self.assertEqual({
      'k1': 123.0,
      'k2': 456.0,
      'k3': 789.0,
      'k4': 789.0,
      'k5': 1.0,
      'k6': 0.0,
    }, dict(d.num_values))
    self.assertEqual({}, dict(d.string_values))
    self.assertEqual({}, dict(d.binary_values))


  def test_auto(self):
    binary_data = 'テスト'.encode('cp932')

    schema = GenericSchema({}, GenericSchema.AUTO)
    d = schema.transform({
      'k1': '123',
      'k2': 456,
      'k3': '789'.encode(),
      'k4': 'xxx'.encode(),
      'k5': binary_data,
      'k6': True,
      'k7': False,
    })

    self.assertEqual({'k1': '123', 'k6': '1', 'k7': '0'}, dict(d.string_values))
    self.assertEqual({'k2': 456}, dict(d.num_values))
    self.assertEqual({'k3': '789'.encode(), 'k4': 'xxx'.encode(), 'k5': binary_data}, dict(d.binary_values))

  def test_infer(self):
    binary_data = 'テスト'.encode('cp932')

    schema = GenericSchema({}, GenericSchema.INFER)
    d = schema.transform({
      'k1': '123',
      'k2': 456,
      'k3': '789'.encode(),
      'k4': 'xxx'.encode(),
      'k5': binary_data,
      'k6': True,
      'k7': False,
    })

    self.assertEqual({'k4': 'xxx', 'k6': '1', 'k7': '0'}, dict(d.string_values))
    self.assertEqual({'k1': 123, 'k2': 456, 'k3': 789}, dict(d.num_values))
    self.assertEqual({'k5': binary_data}, dict(d.binary_values))

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

  def test_transform_as_datum(self):
    d = Datum()

    schema = GenericSchema({
      'k1': GenericSchema.NUMBER,
    }, GenericSchema.IGNORE)
    d2 = schema._transform_as_datum({
      'k1': '123',
      'k2': 456,
    }, d)

    self.assertEqual(d2, d)
    self.assertEqual({'k1': 123}, dict(d.num_values))

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

  def test_invalid_predict(self):
    schema = GenericSchema({'k1': GenericSchema.STRING})
    self.assertRaises(ValueError, schema.predict, {'k1': object()}, True)

  def test_invalid_transform(self):
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

  def test_invalid_infinite_static(self):
    loader = StubInfiniteLoader()  # infinite loader
    self.assertRaises(RuntimeError, BaseDataset, loader, None, True)  # cannot be static

  def test_predict(self):
    loader = StubLoader()
    ds = BaseDataset(loader, self.SCHEMA)
    self.assertRaises(NotImplementedError, ds._predict, {})

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

  def test_convert(self):
    loader = StubLoader()
    ds1 = BaseDataset(loader, self.SCHEMA)
    def f(d):
      new_d = {}
      for (k, v) in d.items():
        new_d[k] = d[k] + 1
      return new_d
    ds2 = ds1.convert(lambda data: [f(d) for d in data])
    self.assertEqual(1, ds1[0].num_values[0][1])
    self.assertEqual(2, ds2[0].num_values[0][1])

  def test_convert_empty(self):
    loader = StubLoader()
    ds1 = BaseDataset(loader, self.SCHEMA)
    ds2 = ds1.convert(lambda data: [None for d in data])  # ds2 should be empty
    for d in ds2:
      self.fail()

  def test_invalid_convert(self):
    loader = StubLoader()
    ds1 = BaseDataset(loader, self.SCHEMA)
    self.assertRaises(RuntimeError, ds1.convert, lambda x: None)

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

    self.assertRaises(RuntimeError, ds.shuffle, 0)
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

  def test_index_access(self):
    loader = StubLoader()
    ds = BaseDataset(loader, self.SCHEMA)
    self.assertTrue(isinstance(ds[0], jubatus.common.Datum))
    self.assertTrue(isinstance(ds[0:1], BaseDataset))

class TestBaseService(TestCase):
  def test_simple(self):
    service = BaseService()
    self.assertRaises(NotImplementedError, service.name)
    self.assertRaises(NotImplementedError, service._client)
    self.assertRaises(NotImplementedError, service._client_class)

  def test_stub(self):
    service = StubService()
    self.assertRaises(RuntimeError, service.run, StubConfig())  # juba_stub does not exist
    service.stop()

class TestBaseConfig(TestCase):
  def test_base(self):
    self.assertRaises(NotImplementedError, BaseConfig)

  def test_simple(self):
    config = StubConfig()
    self.assertEqual({'test': 1.0}, config)

class TestGenericConfg(TestCase):
  def test_base(self):
    self.assertRaises(NotImplementedError, GenericConfig)
    self.assertRaises(NotImplementedError, GenericConfig.methods)
    self.assertRaises(NotImplementedError, GenericConfig._default_method)
    self.assertRaises(NotImplementedError, GenericConfig._default_parameter, None)
    self.assertTrue(isinstance(GenericConfig._default_converter(), dict))

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

  def test_without_converter(self):
    config = StubGenericConfigWithoutConverter(converter={})
    self.assertEqual('test', config['method'])
    self.assertTrue('parameter' not in config)
    self.assertEqual({}, config['converter'])

  def test_clear_converter(self):
    config = StubGenericConfig()
    self.assertTrue('unigram' in config['converter']['string_types'])
    config.clear_converter()
    self.assertFalse('unigram' in config['converter']['string_types'])

  def test_add_mecab(self):
    config = StubGenericConfig()
    self.assertFalse('mecab2' in config['converter']['string_types'])
    config.add_mecab(name='mecab2', ngram=2, base=True, include_features='名詞,*', exclude_features=['動詞,*', '形容詞,*'])
    self.assertTrue('mecab2' in config['converter']['string_types'])
    self.assertEqual('2', config['converter']['string_types']['mecab2']['ngram'])
    self.assertEqual('true', config['converter']['string_types']['mecab2']['base'])
    self.assertEqual('名詞,*', config['converter']['string_types']['mecab2']['include_features'])
    self.assertEqual('動詞,*|形容詞,*', config['converter']['string_types']['mecab2']['exclude_features'])

    self.assertFalse('mecab3' in config['converter']['string_types'])
    config.add_mecab(name='mecab3', ngram="3", base=False, include_features=['名詞,*','動詞,*'], exclude_features='動詞,*|名詞,固有名詞,*')
    self.assertTrue('mecab3' in config['converter']['string_types'])
    self.assertEqual('3', config['converter']['string_types']['mecab3']['ngram'])
    self.assertEqual('false', config['converter']['string_types']['mecab3']['base'])
    self.assertEqual('名詞,*|動詞,*', config['converter']['string_types']['mecab3']['include_features'])
    self.assertEqual('動詞,*|名詞,固有名詞,*', config['converter']['string_types']['mecab3']['exclude_features'])

class UtilsTest(TestCase):
  def test_softmax(self):
    res = Utils.softmax([0])
    self.assertEqual(res, [1.0])

    res = Utils.softmax([0,1])
    self.assertEqual(res, [(1 / (1 + math.e)), (math.e / (1 + math.e))])

    res = Utils.softmax([-5, 0, 5])
    self.assertEqual(sum(res), 1.0)

    # should not overflow for large numbers
    res = Utils.softmax([-100000000, 100000000])
    self.assertEqual(sum(res), 1.0)
