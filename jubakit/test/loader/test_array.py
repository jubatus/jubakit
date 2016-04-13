# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.loader.array import ArrayLoader, ZipArrayLoader

class ArrayLoaderTest(TestCase):
  def test_simple(self):
    loader = ArrayLoader(
      [['1','2'], ['3','4']],
      ['k1','k2']
    )
    for row in loader:
      self.assertEqual(set(['k1','k2']), set(row.keys()))
      if row['k1'] == '1':
        self.assertEqual('2', row['k2'])
      elif row['k1'] == '3':
        self.assertEqual('4', row['k2'])
      else:
        self.fail('unexpected row: {0}'.format(row))

  def test_auto_feature_name(self):
    loader = ArrayLoader([['1','2']])
    for row in loader:
      self.assertEqual(set(['v0', 'v1']), set(row.keys()))
      self.assertEqual('1', row['v0'])
      self.assertEqual('2', row['v1'])

class ZipArrayLoaderTest(TestCase):
  def test_simple(self):
    loader = ZipArrayLoader(
      [['1','2','3'], ['x', 'y', 'z']],
      ['k1', 'k2']
    )
    self._check_loader(loader)

  def test_kwargs(self):
    loader = ZipArrayLoader(
      k1=['1','2','3'],
      k2=['x', 'y', 'z'],
    )
    self._check_loader(loader)

  def test_mixed(self):
    loader = ZipArrayLoader(
      [['1','2','3']],
      ['k1'],
      k2=['x', 'y', 'z']
    )
    self._check_loader(loader)

  def test_error(self):
    self.assertRaises(RuntimeError, ZipArrayLoader, [['1','2','3'], ['x', 'y', 'z']], ['k1'])

  def _check_loader(self, loader):
    for row in loader:
      self.assertEqual(set(['k1', 'k2']), set(row.keys()))
      if row['k1'] == '1':
        self.assertEqual('x', row['k2'])
      elif row['k1'] == '2':
        self.assertEqual('y', row['k2'])
      elif row['k1'] == '3':
        self.assertEqual('z', row['k2'])
      else:
        self.fail('unexpected row')
