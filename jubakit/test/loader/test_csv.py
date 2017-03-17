# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase
from tempfile import NamedTemporaryFile as TempFile

from jubakit.loader.csv import CSVLoader

from .. import requirePython3

class CSVLoaderTest(TestCase):
  def test_simple(self):
    with TempFile() as f:
      f.write("k1,\"k2\",k3\n1,2,3\n4,5,6".encode('utf-8'))
      f.flush()
      loader = CSVLoader(f.name)
      lines = 0
      for row in loader:
        lines += 1
        self.assertEqual(set(['k1','k2','k3']), set(row.keys()))
        if row['k1'] == '1':
          self.assertEqual('2', row['k2'])
          self.assertEqual('3', row['k3'])
        elif row['k1'] == '4':
          self.assertEqual('5', row['k2'])
          self.assertEqual('6', row['k3'])
        else:
          self.fail('unexpected row')
      self.assertEqual(2, lines)

  def test_guess_header(self):
    with TempFile() as f:
      f.write("k1|k2|k3\n1|2|3".encode())
      f.flush()
      loader = CSVLoader(f.name, fieldnames=True, delimiter='|')
      self.assertEqual([{'k1': '1', 'k2': '2', 'k3': '3'}], list(loader))

  def test_noheader(self):
    with TempFile() as f:
      f.write("1|\"2\"|3\n\"4\"|5|\"6\"".encode('utf-8'))
      f.flush()
      loader = CSVLoader(f.name, False, delimiter='|')
      lines = 0
      for row in loader:
        lines += 1
        self.assertEqual(set(['c0','c1','c2']), set(row.keys()))
        if row['c0'] == '1':
          self.assertEqual('2', row['c1'])
          self.assertEqual('3', row['c2'])
        elif row['c0'] == '4':
          self.assertEqual('5', row['c1'])
          self.assertEqual('6', row['c2'])
        else:
          self.fail('unexpected row')
      self.assertEqual(2, lines)

  def test_cp932(self):
    with TempFile() as f:
      f.write("列1,列2\nテスト1,テスト2\n".encode('cp932'))
      f.flush()
      # predict field names from 1st row
      loader = CSVLoader(f.name, None, 'cp932', delimiter=',')
      lines = 0
      for row in loader:
        lines += 1
        self.assertEqual('テスト1', row['列1'])
        self.assertEqual('テスト2', row['列2'])
      self.assertEqual(1, lines)

  def test_cp932_seq_fieldnames(self):
    with TempFile() as f:
      f.write("テスト1,テスト2\nテスト1,テスト2".encode('cp932'))
      f.flush()
      # assign sequential field names
      loader = CSVLoader(f.name, False, 'cp932', delimiter=',')
      lines = 0
      for row in loader:
        lines += 1
        self.assertEqual('テスト1', row['c0'])
        self.assertEqual('テスト2', row['c1'])
      self.assertEqual(2, lines)

  def test_cp932_manual_fieldnames(self):
    with TempFile() as f:
      f.write("テスト1,テスト2\nテスト1,テスト2".encode('cp932'))
      f.flush()
      # assign field names statically
      loader = CSVLoader(f.name, ['列1', '列2'], 'cp932', delimiter=',')
      lines = 0
      for row in loader:
        lines += 1
        self.assertEqual('テスト1', row['列1'])
        self.assertEqual('テスト2', row['列2'])
      self.assertEqual(2, lines)

  def test_restkey(self):
    with TempFile() as f:
      f.write("テスト1,テスト2\nテスト1,テスト2".encode('utf-8'))
      f.flush()
      loader = CSVLoader(f.name, ['c1'], 'utf-8', restkey='garbage')
      for row in loader:
        self.assertEqual('テスト1', row['c1'])
        self.assertEqual(['テスト2'], row['garbage'])

  def test_restval(self):
    with TempFile() as f:
      f.write("テスト1,テスト2\nテスト1,テスト2".encode('utf-8'))
      f.flush()
      loader = CSVLoader(f.name, ['c1', 'c2', 'c3'], 'utf-8', restval='<blank>')
      for row in loader:
        self.assertEqual('テスト1', row['c1'])
        self.assertEqual('テスト2', row['c2'])
        self.assertEqual('<blank>', row['c3'])

  @requirePython3
  def test_unicode_separator(self):
    with TempFile() as f:
      f.write("v1★v2\ns1★s2\n".encode('utf-8'))
      f.flush()
      loader = CSVLoader(f.name, delimiter='★')
      lines = 0
      for row in loader:
        lines += 1
        self.assertEqual('s1', row['v1'])
        self.assertEqual('s2', row['v2'])
      self.assertEqual(1, lines)
