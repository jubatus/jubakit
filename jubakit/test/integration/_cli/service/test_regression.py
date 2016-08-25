# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.dumb import Regression
from jubakit._cli.service import RegressionCLI

from .base import BaseCLITestCase

class RegressionCLITest(BaseCLITestCase):
  def setUp(self):
    self._service = Regression.run(Regression.CONFIG)

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    self._ok([
      'clear',
      'train 10 x 1 y 1',
      'train -10 x -1 y -1',
      'estimate x 100 y 100',
    ])

  def test_fail(self):
    self._fail([
      'train x',
      'train 10 x',
      'estimate x 100 y',
    ])
