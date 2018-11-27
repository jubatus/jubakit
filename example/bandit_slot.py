#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, \
                       print_function, unicode_literals

"""
Using Classifier and CSV file
========================================

This is an simple example of Bandit service.

The player `Jubatun` tries to maximize the cumulative reward of
a sequence of slot machine plays by multi-armed bandit algorithm.

You can try various simulation settings by modifying the slot machine setting.
Let's edit lines 67-72 and enjoy!
"""

import random

from jubakit.bandit import Bandit, Config


class Slot(object):
    """Slot machine."""

    def __init__(self, probability, average, stddev):
        """
        Initialize slot machine.

        :param float probability: Hit probability.
        :param float average: Average of a gaussian distribution.
        :param float stddev: Standard deviation of a gaussian distribution.
        :return: self
        """
        self.probability = probability
        self.average = average
        self.stddev = stddev

    def hit(self):
        """
        This slot machine hits with the given probability.

        :return bool: Whether this slot machine hits or not.
        """
        if random.random() < self.probability:
            return True
        else:
            return False

    def reward(self):
        """
        A reward is determined based on
        the given average and standard deviation.

        :return float: A reward.
        """
        if self.hit():
            return random.gauss(self.average, self.stddev)
        else:
            return 0.0


# Experimental config.
# Which slot machine should we choose?
iteration = 1000
slots = {
    'bad': Slot(0.1, 50, 10),  # E[R] = 5: bad arm
    'normal': Slot(0.01, 600, 100),  # E[R] = 6: normal arm
    'good': Slot(0.001, 8000, 1000)  # E[R] = 8: good arm
}

# Launch bandit service.
player = 'Jubatan'
config = Config(method='epsilon_greedy', parameter={'epsilon': 0.1})
bandit = Bandit.run(config)

# Initialize bandit settings.
bandit.reset(player)
for name, slot in slots.items():
    bandit.register_arm(name)

# Select arms and get rewards.
cumulative_reward = 0
for i in range(iteration):
    arm = bandit.select_arm(player)
    reward = float(slots[arm].reward())
    bandit.register_reward(player, arm, reward)
    cumulative_reward += reward

# Show result.
arm_info = bandit.get_arm_info(player)
frequencies = {name: info.trial_count for name, info in arm_info.items()}

print('cumulative reward: {0:.2f}'.format(cumulative_reward))
print('slot frequencies: {0}'.format(frequencies))
