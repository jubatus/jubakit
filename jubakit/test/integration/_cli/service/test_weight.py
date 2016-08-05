# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.weight import Weight, Config
from jubakit._cli.service import WeightCLI

from .base import BaseCLITestCase

class WeightCLITest(BaseCLITestCase):
  def setUp(self):
    self._service = Weight.run(Config())

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    self._ok([
      'clear',
      'update x 1 y 1',
      'calc_weight x 1 y 1',
    ])

  def test_fail(self):
    self._fail([
      'update x',
      'calc_weight x 1 y',
    ])
