# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from jubatus.stat.types import *

from .generic import GenericCLI
from ..args import Arguments
from ..util import *
from ..._stdio import print

class StatCLI(GenericCLI):
  @classmethod
  def _name(cls):
    return 'stat'

  @Arguments(str, float)
  def do_push(self, key, value):
    """Syntax: push key value
    Add value for the specified key.
    """
    result = self.client.push(key, value)
    if not result:
      print("Failed")

  @Arguments(str)
  def do_sum(self, key):
    """Syntax: sum key
    Get sum for the specified key.
    """
    print(self.client.sum(key))

  @Arguments(str)
  def do_stddev(self, key):
    """Syntax: stddev key
    Get stddev for the specified key.
    """
    print(self.client.stddev(key))

  @Arguments(str)
  def do_max(self, key):
    """Syntax: max key
    Get max for the specified key.
    """
    print(self.client.max(key))

  @Arguments(str)
  def do_min(self, key):
    """Syntax: min key
    Get min for the specified key.
    """
    print(self.client.min(key))

  @Arguments(str)
  def do_entropy(self, key):
    """Syntax: entropy key
    Get entropy for the specified key.
    """
    print(self.client.entropy(key))

  @Arguments(str, int, float)
  def do_moment(self, key, n, c):
    """Syntax: moment key n c
    Get n-th moment about c of values in the specified key.
    """
    print(self.client.moment(key, n, c))
