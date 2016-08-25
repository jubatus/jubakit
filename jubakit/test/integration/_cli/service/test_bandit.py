# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.dumb import Bandit
from jubakit._cli.service import BanditCLI

from .base import BaseCLITestCase

class BanditCLITest(BaseCLITestCase):
  def setUp(self):
    self._service = Bandit.run(Bandit.CONFIG)

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    self._ok([
      'clear',
      'register_arm a1',
      'register_arm a2',
      'register_arm a3',
      'delete_arm a3',
      'select_arm p1',
      'select_arm p2',
      'register_reward p1 a1 100',
      'register_reward p2 a2 100',
      'get_arm_info p1',
      'reset p1',
    ])
    self.assertEqual(set(self._service._client().get_arm_info('p1').keys()), set(['a1', 'a2']))

  def test_fail(self):
    self._fail([
      'register_arm',
      'register_arm x y',
      'delete_arm',
      'select_arm',
      'register_reward',
      'register_reward p a x',
      'get_arm_info',
      'reset',
    ])
