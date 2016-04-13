# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.loader.array import ArrayLoader, ZipArrayLoader
from jubakit.loader.chain import SupervisedDataChainLoader

class SupervisedDataChainLoaderTest(TestCase):
  def test_simple(self):
    loader = SupervisedDataChainLoader(
      ArrayLoader([[0,1],[2,3],[4,5]], ['v1','v2']),
      ZipArrayLoader(_label=[0,1,0]),
      ['X','Y'],
    )
    for row in loader:
      self.assertEqual(set(['v1','v2','_label']), set(row.keys()))
      if row['v1'] == 0:
        self.assertEqual(1,   row['v2'])
        self.assertEqual('X', row['_label'])
      elif row['v1'] ==2:
        self.assertEqual(3,   row['v2'])
        self.assertEqual('Y', row['_label'])
      elif row['v1'] == 4:
        self.assertEqual(5,   row['v2'])
        self.assertEqual('X', row['_label'])
      else:
        self.fail('unexpected row')
