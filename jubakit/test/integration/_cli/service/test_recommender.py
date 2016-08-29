# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.dumb import Recommender
from jubakit._cli.service import RecommenderCLI

from .base import BaseCLITestCase

class RecommenderCLITest(BaseCLITestCase):
  def setUp(self):
    self._service = Recommender.run(Recommender.CONFIG)

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    self._ok([
      'clear',
      'update_row p1 x 1 y "foo"',
      'update_row p2 x 2 y "bar"',
      'complete_row_from_id p1',
      'complete_row_from_datum x 1',
      'similar_row_from_id p1',
      'similar_row_from_datum x 1',
      'decode_row p1',
      'get_all_rows',
      'calc_similarity x 1 y "foo" |',
      'calc_similarity x 1 y "foo" | x 2 y "bar"',
      'calc_l2norm x 1',
      'max_results',
      'max_results 100',
    ])
    self.assertEqual(set(self._service._client().get_all_rows()), set(['p1', 'p2']))

  def test_fail(self):
    self._fail([
      'update_row p1 x',
      'complete_row_from_id',
      'complete_row_from_datum x 1 y',
      'similar_row_from_id x y',
      'similar_row_from_datum x',
      'decode_row',
      'get_all_rows foo',
      'calc_similarity x 1 y',
      'calc_similarity x 1 y "foo"',
      'calc_similarity x 1 y "foo" | x',
      'calc_l2norm x',
      'max_results abc',
      'max_results 100 abc',
    ])
