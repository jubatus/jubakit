# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.bandit import Bandit, Config

from . import requireEmbedded


class BanditTest(TestCase):

  def test_simple(self):
    Bandit()

  def test_simple_launch(self):
    Bandit.run(Config())

  @requireEmbedded
  def test_embedded(self):
    Bandit.run(Config(), embedded=True)

  def test_register_arm(self):
    bandit = Bandit.run(Config())
    ret = bandit.register_arm(1)
    self.assertIsInstance(ret, bool)

  def test_delete_arm(self):
    bandit = Bandit.run(Config())
    bandit.register_arm(1)
    ret = bandit.delete_arm(1)
    self.assertIsInstance(ret, bool)

  def test_select_arm(self):
    bandit = Bandit.run(Config())
    bandit.register_arm(1)
    ret = bandit.select_arm('player')
    self.assertEqual(ret, str(1))

  def test_register_reward(self):
    bandit = Bandit.run(Config())
    bandit.register_arm(1)
    bandit.select_arm('player')
    ret = bandit.register_reward('player', 1, 10)
    self.assertIsInstance(ret, bool)

  def test_get_arm_info(self):
    from jubatus.bandit.types import ArmInfo
    bandit = Bandit.run(Config())
    bandit.register_arm(1)
    bandit.select_arm('player')
    ret = bandit.get_arm_info('player')
    self.assertIsInstance(ret, dict)
    for name, info in ret.items():
      self.assertIsInstance(name, str)
      self.assertIsInstance(info, ArmInfo)

  def test_reset(self):
    bandit = Bandit.run(Config())
    bandit.register_arm(1)
    bandit.select_arm('player')
    bandit.register_reward('player', 1, 10)
    ret = bandit.reset('player')
    self.assertIsInstance(ret, bool)


class ConfigTest(TestCase):

  def test_simple(self):
    config = Config()
    self.assertEqual('epsilon_greedy', config['method'])

  def test_methods(self):
    config = Config()
    self.assertIsInstance(config.methods(), list)

  def test_default(self):
    config = Config.default()
    self.assertEqual('epsilon_greedy', config['method'])

  def test_method_params(self):
    for method in Config.methods():
      self.assertTrue(
        'assume_unrewarded' in Config(method=method)['parameter'])
    self.assertTrue('epsilon' in Config(method='epsilon_greedy')['parameter'])
    self.assertTrue('tau' in Config(method='softmax')['parameter'])
    self.assertTrue('gamma' in Config(method='exp3')['parameter'])

  def test_invalid_method(self):
    self.assertRaises(
      RuntimeError, Config._default_parameter, 'invalid_method')
