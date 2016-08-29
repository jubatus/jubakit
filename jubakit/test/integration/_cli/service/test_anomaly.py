# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.anomaly import Anomaly, Config
from jubakit._cli.service import AnomalyCLI

from .base import BaseCLITestCase

class AnomalyCLITest(BaseCLITestCase):
  def setUp(self):
    self._service = Anomaly.run(Config())

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    self._ok([
      'clear',
      'add x 1 y 1',
      'update p1 x 1 y 2',
      'overwrite p2 x 1 y 3',
      'calc_score x 1 y 4',
      'get_all_rows',
    ])
    self.assertEqual(set(self._service._client().get_all_rows()), set(['0', 'p1', 'p2']))

  def test_fail(self):
    self._fail([
      'train',
      'add x 1 y',
      'update x 1',
      'overwrite x 1',
      'calc_score x',
      'get_all_rows foo',
      'clear_row',
    ])
