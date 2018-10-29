# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.loader.postgresql import PostgreSQLoader
from jubakit.loader.postgresql import PostgreSQLAuthHandler

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class PostgreSQLoaderTest(TestCase):
  auth = PostgreSQLAuthHandler(user='postgres', password='postgres', host='localhost', port='5432')

  def setUp(self):
    print("setUp")
    connection = psycopg2.connect("host=localhost port=5432 user=postgres password=postgres")
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute("DROP DATABASE IF EXISTS test;")
    cursor.execute("CREATE DATABASE test;")

    cursor.execute("DROP TABLE IF EXISTS test;")
    cursor.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
    cursor.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abcdef"))
    cursor.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (200, "ghijkl"))
    cursor.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (300, "mnopqr"))

    connection.commit()
    connection.close()

    connection = psycopg2.connect("dbname=test host=localhost port=5432 user=postgres password=postgres")
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS test2;")
    cursor.execute("CREATE TABLE test2 (id serial PRIMARY KEY, num integer, data varchar);")
    cursor.execute("INSERT INTO test2 (num, data) VALUES (%s, %s)", (1000, "st"))
    cursor.execute("INSERT INTO test2 (num, data) VALUES (%s, %s)", (2000, "uv"))
    cursor.execute("INSERT INTO test2 (num, data) VALUES (%s, %s)", (3000, "wx"))

    connection.commit()
    connection.close()

  def test_simple(self):
    loader = PostgreSQLoader(self.auth, table='test')
    for row in loader:
      self.assertEqual(set(['id','num', 'data']), set(row.keys()))
      if row['id'] == 1:
        self.assertEqual(100, row['num'])
        self.assertEqual('abcdef', row['data'])
      elif row['id'] == 2:
        self.assertEqual(200, row['num'])
        self.assertEqual('ghijkl', row['data'])
      elif row['id'] == 3:
        self.assertEqual(300, row['num'])
        self.assertEqual('mnopqr', row['data'])
      else:
        self.fail('unexpected row: {0}'.format(row))

  def test_specify_dbname(self):
    self.auth = PostgreSQLAuthHandler(dbname='test', user='postgres', password='postgres', host='localhost', port='5432')
    loader = PostgreSQLoader(self.auth, table='test2')
    for row in loader:
      self.assertEqual(set(['id','num', 'data']), set(row.keys()))
      if row['id'] == 1:
        self.assertEqual(1000, row['num'])
        self.assertEqual('st', row['data'])
      elif row['id'] == 2:
        self.assertEqual(2000, row['num'])
        self.assertEqual('uv', row['data'])
      elif row['id'] == 3:
        self.assertEqual(3000, row['num'])
        self.assertEqual('wx', row['data'])
      else:
        self.fail('unexpected row: {0}'.format(row))

  def tearDown(self):
    print("tearDown")
    connection = psycopg2.connect("host=localhost port=5432 user=postgres password=postgres")
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()

    cursor.execute("DROP DATABASE test;")
    cursor.execute("DROP TABLE test;")
    connection.commit()
    connection.close()
