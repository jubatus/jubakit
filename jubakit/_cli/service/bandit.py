# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from jubatus.bandit.types import *

from .generic import GenericCLI
from ..args import Arguments
from ..util import *
from ..._stdio import print

class BanditCLI(GenericCLI):
  @classmethod
  def _name(cls):
    return 'bandit'

  @Arguments(str)
  def do_register_arm(self, arm_id):
    """Syntax: register_arm arm_id
    Adds the specified arm.
    """
    self.client.register_arm(arm_id)

  @Arguments(str)
  def do_delete_arm(self, arm_id):
    """Syntax: delete_arm arm_id
    Deletes the specified arm.
    """
    self.client.delete_arm(arm_id)

  @Arguments(str)
  def do_select_arm(self, player_id):
    """Syntax: select_arm player_id
    Select the specified arm and return the next best guess.
    """
    print(self.client.select_arm(player_id))

  @Arguments(str, str, float)
  def do_register_reward(self, player_id, arm_id, reward):
    """Syntax: register_reward player_id arm_id reward
    Registers the reward for the specified player and ID.
    """
    print(self.client.register_reward(player_id, arm_id, reward))

  @Arguments(str)
  def do_get_arm_info(self, player_id):
    """Syntax: get_arm_info player_id
    Returns the arm info for the specified ID.
    """
    print(self.client.get_arm_info(player_id))

  @Arguments(str)
  def do_reset(self, player_id):
    """Syntax: reset player_id
    Resets the specified player record.
    """
    print(self.client.reset(player_id))
