# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.dumb import Stat
from jubakit._cli.service import StatCLI

from .base import BaseCLITestCase

class StatCLITest(BaseCLITestCase):
  def setUp(self):
    self._service = Stat.run(Stat.CONFIG)

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    self._ok([
      'clear',
      'push x 1',
      'push x 2',
      'push y 3',
      'push y 4',
      'sum x',
      'stddev y',
      'max x',
      'min y',
      'entropy x',
      'moment y 0 1',
    ])
    self.assertEqual(self._service._client().max('x'), 2)
    self.assertEqual(self._service._client().max('y'), 4)

  def test_fail(self):
    self._fail([
      'push',
      'push x 1 2',
      'sum',
      'stddev',
      'max',
      'min',
      'entropy',
      'moment x x x x',
    ])
