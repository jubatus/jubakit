# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.loader.array import ArrayLoader, ZipArrayLoader
from jubakit.loader.chain import MergeChainLoader, ValueMapChainLoader, ConcatLoader

class MergeChainLoaderTest(TestCase):
  def test_simple(self):
    loader = MergeChainLoader(
      ArrayLoader([[0,1],[2,3],[4,5]], ['v1','v2']),
      ArrayLoader([[0,1],[2,3],[4,5]], ['v3','v4']),
    )
    for row in loader:
      self.assertEqual(set(['v1','v2','v3','v4']), set(row.keys()))
      if row['v1'] == 0:
        self.assertEqual(1, row['v2'])
        self.assertEqual(0, row['v3'])
        self.assertEqual(1, row['v4'])
      elif row['v1'] ==2:
        self.assertEqual(3, row['v2'])
        self.assertEqual(2, row['v3'])
        self.assertEqual(3, row['v4'])
      elif row['v1'] == 4:
        self.assertEqual(5, row['v2'])
        self.assertEqual(4, row['v3'])
        self.assertEqual(5, row['v4'])
      else:
        self.fail('unexpected row: {0}'.format(row))

class ValueMapChainLoaderTest(TestCase):
  def test_simple(self):
    loader = ValueMapChainLoader(
      ArrayLoader([[0,1],[2,3],[4,5]], ['v1','v2']),
      'v2',
      {1: '_test1', 3: '_test3', 5: '_test5'}
    )
    for row in loader:
      self.assertEqual(set(['v1','v2']), set(row.keys()))
      if row['v1'] == 0:
        self.assertEqual('_test1', row['v2'])
      elif row['v1'] == 2:
        self.assertEqual('_test3', row['v2'])
      elif row['v1'] == 4:
        self.assertEqual('_test5', row['v2'])
      else:
        self.fail('unexpected row: {0}'.format(row))

class ConcatLoaderTest(TestCase):
  def test_simple(self):
    loader = ConcatLoader(
      ZipArrayLoader(v1=[1,2,3], v2=[11,12,13]),
      ZipArrayLoader(v1=[4,5,6], v2=[14,15,16]),
    )
    count = 0
    for row in loader:
      count += 1
      self.assertEqual(set(['v1', 'v2']), set(row.keys()))
      self.assertEqual(row['v1'], count)
      self.assertEqual(row['v2'], count + 10)
    self.assertEqual(count, 6)
