# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import jubatus
import jubatus.embedded

from .base import BaseService, GenericConfig


class Bandit(BaseService):
  """
  Bandit service.
  """

  @classmethod
  def name(cls):
    return 'bandit'

  @classmethod
  def _client_class(cls):
    return jubatus.bandit.client.Bandit

  @classmethod
  def _embedded_class(cls):
    return jubatus.embedded.Bandit

  def register_arm(self, arm_id):
    arm_id = str(arm_id)
    return self._client().register_arm(arm_id)

  def delete_arm(self, arm_id):
    arm_id = str(arm_id)
    return self._client().delete_arm(arm_id)

  def select_arm(self, player_id):
    player_id = str(player_id)
    return self._client().select_arm(player_id)

  def register_reward(self, player_id, arm_id, reward):
    arm_id = str(arm_id)
    player_id = str(player_id)
    reward = float(reward)
    return self._client().register_reward(player_id, arm_id, reward)

  def get_arm_info(self, player_id):
    player_id = str(player_id)
    return self._client().get_arm_info(player_id)

  def reset(self, player_id):
    player_id = str(player_id)
    return self._client().reset(str(player_id))


class Config(GenericConfig):
  """
  Configuration to run Bandit service.
  """

  @classmethod
  def methods(cls):
    return [
      'epsilon_greedy',
      'epsilon_decreasing',
      'ucb1',
      'softmax',
      'exp3',
      'ts'
    ]

  @classmethod
  def _default_method(cls):
    return 'epsilon_greedy'

  @classmethod
  def _default_parameter(cls, method):
    params = {
      'assume_unrewarded': False
    }
    if method in ('epsilon_greedy',):
      params['epsilon'] = 0.1
    elif method in ('softmax',):
      params['tau'] = 0.05
    elif method in ('exp3',):
      params['gamma'] = 0.1
    elif method not in ('epsilon_decreasing', 'ucb1', 'ts'):
      raise RuntimeError('unknown method: {0}'.format(method))
    return params

  @classmethod
  def _default(cls, cfg):
    cfg.clear()

    method = cls._default_method()
    parameter = cls._default_parameter(method)

    if method is not None:
      cfg['method'] = method
    if parameter is not None:
      cfg['parameter'] = parameter
