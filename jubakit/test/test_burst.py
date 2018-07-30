# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.burst import KeywordSchema, KeywordDataset
from jubakit.burst import DocumentSchema, DocumentDataset
from jubakit.burst import Burst, Config
from jubakit.compat import *

from . import requireSklearn, requireEmbedded
from jubakit.base import BaseLoader


class KeywordSchemaTest(TestCase):

  def test_simple(self):
    schema = KeywordSchema({
      'keyword': KeywordSchema.KEYWORD,
      'scaling': KeywordSchema.SCALING,
      'gamma': KeywordSchema.GAMMA
    })
    keyword = 'test'
    scaling = 1.1
    gamma = 0.1
    tf_keyword, tf_scaling, tf_gamma = schema.transform(
      {'keyword': keyword, 'scaling': scaling, 'gamma': gamma})
    self.assertEqual(keyword, tf_keyword)
    self.assertEqual(scaling, tf_scaling)
    self.assertEqual(gamma, tf_gamma)

  def test_illegal_init(self):
    self.assertRaises(RuntimeError, KeywordSchema, {
      'k1': KeywordSchema.KEYWORD,
      'k2': KeywordSchema.KEYWORD,
    })

    self.assertRaises(RuntimeError, KeywordSchema, {
      's1': KeywordSchema.SCALING,
      's2': KeywordSchema.SCALING,
    })

    self.assertRaises(RuntimeError, KeywordSchema, {
      'g1': KeywordSchema.GAMMA,
      'g2': KeywordSchema.GAMMA,
    })

  def test_illegal_row(self):
    self.assertRaises(RuntimeError, self._test_row, None, None, None)
    self.assertRaises(ValueError, self._test_row, 'test', 'hoge', None)
    self.assertRaises(ValueError, self._test_row, 'test', None, 'hoge')
    self.assertRaises(ValueError, self._test_row, 'test', 0.1, None)
    self.assertRaises(ValueError, self._test_row, 'test', '0.1', None)
    self.assertRaises(ValueError, self._test_row, 'test', None, -0.1)
    self.assertRaises(ValueError, self._test_row, 'test', None, '-0.1')

  def _test_row(self, keyword, scaling, gamma):
    schema = KeywordSchema({
      'keyword': KeywordSchema.KEYWORD,
      'scaling': KeywordSchema.SCALING,
      'gamma': KeywordSchema.GAMMA
    })
    return schema.transform(
      {'keyword': keyword, 'scaling': scaling, 'gamma': gamma})


class DocumentSchemaTest(TestCase):

  def test_simple(self):

    position = 1
    text = 'text'
    tf_position, tf_text = self._test_row(position, text)
    self.assertEqual(position, tf_position)
    self.assertEqual(text, tf_text)

    tf_position, tf_text = self._test_row(str(position), text)
    self.assertEqual(position, tf_position)
    self.assertEqual(text, tf_text)

    tf_position, tf_text = self._test_row(position, None)
    self.assertEqual(position, tf_position)
    self.assertEqual('', tf_text)

  def test_illegal_init(self):
    self.assertRaises(RuntimeError, DocumentSchema, {
      'p1': DocumentSchema.POSITION,
      'p2': DocumentSchema.POSITION,
    })

    self.assertRaises(RuntimeError, DocumentSchema, {
      't1': DocumentSchema.TEXT,
      't2': DocumentSchema.TEXT,
    })

  def test_illegal_row(self):
    self.assertRaises(RuntimeError, self._test_row, None, None)
    self.assertRaises(ValueError, self._test_row, 'position', None)

  def _test_row(self, position, text):
    schema = DocumentSchema({
      'position': DocumentSchema.POSITION,
      'text': DocumentSchema.TEXT
    })
    return schema.transform(
      {'position': position, 'text': text})


class StubKeywordLoader(BaseLoader):

  def __init__(self, keywords, scalings, gammas):
    self.keywords = keywords
    self.scalings = scalings
    self.gammas = gammas

  def rows(self):
    for k, s, g in zip(self.keywords, self.scalings, self.gammas):
      yield {'keyword': k, 'scaling': s, 'gamma': g}
      yield None  # None should be ignored by Dataset


class StubDocumentLoader(BaseLoader):

  def __init__(self, positions, texts):
    self.positions = positions
    self.texts = texts

  def rows(self):
    for p, t in zip(self.positions, self.texts):
      yield {'position': p, 'text': t}
      yield None  # None should be ignored by Dataset


class KeywordDatasetTest(TestCase):

  KEYWORDS = ["foo", "bar", "baz"]
  SCALINGS = ['10', '20', '30']
  GAMMAS = [10, 20, 30]

  def test_simple(self):
    loader = StubKeywordLoader(self.KEYWORDS, self.SCALINGS, self.GAMMAS)
    schema = KeywordSchema({
      'keyword': KeywordSchema.KEYWORD,
      'scaling': KeywordSchema.SCALING,
      'gamma': KeywordSchema.GAMMA
    })
    dataset = KeywordDataset(loader, schema)
    for idx, (keyword, scaling, gamma) in dataset:
      self.assertEqual(self.KEYWORDS[idx], keyword)
      self.assertEqual(float(self.SCALINGS[idx]), scaling)
      self.assertEqual(self.GAMMAS[idx], gamma)


class DocumentDatasetTest(TestCase):

  POSITIONS = [10, 20, 30]
  TEXTS = ["foo", "bar", "baz"]

  def test_simple(self):
    loader = StubDocumentLoader(self.POSITIONS, self.TEXTS)
    schema = DocumentSchema({
      'position': DocumentSchema.POSITION,
      'text': DocumentSchema.TEXT
    })
    dataset = DocumentDataset(loader, schema)
    for idx, (position, text) in dataset:
      self.assertEqual(self.POSITIONS[idx], position)
      self.assertEqual(self.TEXTS[idx], text)


class BurstTest(TestCase):

  def test_simple(self):
    burst = Burst()
    burst.stop()

  @requireEmbedded
  def test_embedded(self):
    burst = Burst.run(Config(), embedded=True)
    burst.stop()

  def test_add_keyword(self):
    burst = Burst.run(Config())
    keyword_dataset = self._make_stub_keyword_dataset()
    for idx, result in burst.add_keyword(keyword_dataset):
      self.assertEqual(result, True)
    burst.stop()

  def test_add_documents(self):
    burst = Burst.run(Config())
    document_dataset = self._make_stub_document_dataset()
    for idx, result in burst.add_documents(document_dataset):
      self.assertEqual(result, 1)
    burst.stop()

  def test_get_results(self):
    burst = Burst.run(Config())
    burst.get_result('keyword')
    burst.stop()

  def test_get_result_at(self):
    burst = Burst.run(Config())
    self.assertRaises(
      ValueError, burst.get_result_at, 'keyword', 'hoge')
    burst.get_result_at('keyword', 10)
    burst.stop()

  def test_get_all_bursted_results(self):
    burst = Burst.run(Config())
    burst.get_all_bursted_results()
    burst.stop()

  def test_get_all_bursted_results_at(self):
    burst = Burst.run(Config())
    self.assertRaises(
      ValueError, burst.get_all_bursted_results_at, 'hoge')
    burst.get_all_bursted_results_at(10)
    burst.stop()

  def test_get_all_keywords(self):
    burst = Burst.run(Config())
    burst.get_all_keywords()
    burst.stop()

  def test_remove_keyword(self):
    burst = Burst.run(Config())
    keyword_dataset = self._make_stub_keyword_dataset()
    for idx, result in burst.add_keyword(keyword_dataset):
      pass
    self.assertEqual(burst.remove_keyword('foo'), True)
    self.assertEqual(burst.remove_keyword('bar'), True)
    self.assertEqual(burst.remove_keyword('baz'), True)
    burst.stop()

  def test_remove_all_keywords(self):
    burst = Burst.run(Config())
    keyword_dataset = self._make_stub_keyword_dataset()
    for idx, result in burst.add_keyword(keyword_dataset):
      pass
    self.assertEqual(burst.remove_all_keywords(), True)
    burst.stop()

  def _make_stub_keyword_dataset(self):
    keywords = ["foo", "bar", "baz"]
    scalings = ['10', '20', '30']
    gammas = [10, 20, 30]

    loader = StubKeywordLoader(keywords, scalings, gammas)
    schema = KeywordSchema({
      'keyword': KeywordSchema.KEYWORD,
      'scaling': KeywordSchema.SCALING,
      'gamma': KeywordSchema.GAMMA
    })
    return KeywordDataset(loader, schema)

  def _make_stub_document_dataset(self):
    positions = [10, 20, 30]
    texts = ["foo", "bar", "baz"]
    loader = StubDocumentLoader(positions, texts)
    schema = DocumentSchema({
      'position': DocumentSchema.POSITION,
      'text': DocumentSchema.TEXT
    })
    return DocumentDataset(loader, schema)


class ConfigTest(TestCase):

  def test_simple(self):
    config = Config()
    self.assertEqual('burst', config['method'])
    import json
    self.assertEqual({
        "window_batch_size": 5,
        "batch_interval": 10,
        "max_reuse_batch_num": 5,
        "costcut_threshold": -1,
        "result_window_rotate_size": 5
      }, config['parameter'])

  def test_methods(self):
    config = Config()
    self.assertTrue(isinstance(config.methods(), list))

  def test_default(self):
    config = Config()
    self.assertEqual('burst', config['method'])

  def test_invalid_method(self):
    self.assertRaises(
      RuntimeError, Config._default_parameter, 'invalid_method')
