# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase
from tempfile import NamedTemporaryFile as TempFile

from jubakit.loader.csv import CSVLoader

class CSVLoaderTest(TestCase):
  def test_simple(self):
    with TempFile() as f:
      f.write("k1,\"k2\",k3\n1,2,3\n4,5,6".encode('utf-8'))
      f.flush()
      loader = CSVLoader(f.name)
      for row in loader:
        self.assertEqual(set(['k1','k2','k3']), set(row.keys()))
        if row['k1'] == '1':
          self.assertEqual('2', row['k2'])
          self.assertEqual('3', row['k3'])
        elif row['k1'] == '4':
          self.assertEqual('5', row['k2'])
          self.assertEqual('6', row['k3'])
        else:
          self.fail('unexpected row')

  def test_guess_header(self):
    with TempFile() as f:
      f.write("k1,k2,k3\n1,2,3".encode())
      f.flush()
      loader = CSVLoader(f.name, fieldnames=True)
      self.assertEqual([{'k1': '1', 'k2': '2', 'k3': '3'}], list(loader))

  def test_noheader(self):
    with TempFile() as f:
      f.write("1,\"2\",3\n\"4\",5,\"6\"".encode('utf-8'))
      f.flush()
      loader = CSVLoader(f.name, False)
      for row in loader:
        self.assertEqual(set(['c0','c1','c2']), set(row.keys()))
        if row['c0'] == '1':
          self.assertEqual('2', row['c1'])
          self.assertEqual('3', row['c2'])
        elif row['c0'] == '4':
          self.assertEqual('5', row['c1'])
          self.assertEqual('6', row['c2'])
        else:
          self.fail('unexpected row')

  def test_cp932(self):
    with TempFile() as f:
      f.write("テスト1,テスト2".encode('cp932'))
      f.flush()
      loader = CSVLoader(f.name, None, 'cp932')
      for row in loader:
        self.assertEqual('テスト1', row['c0'])
        self.assertEqual('テスト2', row['c1'])
