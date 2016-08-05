# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.dumb import NearestNeighbor
from jubakit._cli.service import NearestNeighborCLI

from .base import BaseCLITestCase

class NearestNeighborCLITest(BaseCLITestCase):
  def setUp(self):
    self._service = NearestNeighbor.run(NearestNeighbor.CONFIG)

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    self._ok([
      'clear',
      'set_row p1 x 1 y "foo"',
      'set_row p2 x 2 y "bar"',
      'neighbor_row_from_id p1',
      'neighbor_row_from_datum x 1',
      'similar_row_from_id p1',
      'similar_row_from_datum x 1',
      'get_all_rows',
      'max_results',
      'max_results 100',
    ])
    self.assertEqual(set(self._service._client().get_all_rows()), set(['p1', 'p2']))

  def test_fail(self):
    self._fail([
      'set_row p1 x',
      'neighbor_row_from_id',
      'neighbor_row_from_datum x 1 y',
      'similar_row_from_id x y',
      'similar_row_from_datum x',
      'get_all_rows foo',
      'max_results abc',
      'max_results 100 abc',
    ])
