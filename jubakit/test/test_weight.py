# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.weight import Schema, Dataset, Weight, Config
from jubakit.compat import *

from .stub import *

class SchemaTest(TestCase):
  def test_simple(self):
    schema = Schema({
      'k1': Schema.STRING,
      'k2': Schema.NUMBER,
    })

class DatasetTest(TestCase):
  def test_simple(self):
    row1 = {'k1': 'test1', 'k2': '123'}
    row2 = {'k1': 'test2', 'k2': '456'}
    d = Dataset._predict(row1).transform(row2)

    self.assertEqual(1, len(d.string_values))
    self.assertEqual('k1', d.string_values[0][0])
    self.assertEqual('test2', d.string_values[0][1])

    self.assertEqual(1, len(d.num_values))
    self.assertEqual('k2', d.num_values[0][0])
    self.assertEqual(456, d.num_values[0][1])

class WeightTest(TestCase):
  def test_simple(self):
    weight = Weight()

class ConfigTest(TestCase):
  def test_simple(self):
    config = Config()
