# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.loader.array import ArrayLoader, SupervisedArrayDataLoader

class ArrayLoaderTest(TestCase):
  def test_simple(self):
    loader = ArrayLoader([
      {'k1': '1', 'k2': '2'},
      {'k1': '3', 'k2': '4'},
    ])
    for row in loader:
      self.assertEqual(set(['k1','k2']), set(row.keys()))
      if row['k1'] == '1':
        self.assertEqual('2', row['k2'])
      elif row['k1'] == '3':
        self.assertEqual('4', row['k2'])
      else:
        self.fail('unexpected row')

class SupervisedArrayDataLoaderTest(TestCase):
  def test_simple(self):
    loader = SupervisedArrayDataLoader(
      [[0,1],[2,3],[4,5]],
      ['x','y','z'],
      ['v1','v2'],
      '_label',
      {'x': 'X', 'y': 'Y', 'z': 'Z'},
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
        self.assertEqual('Z', row['_label'])
      else:
        self.fail('unexpected row')
