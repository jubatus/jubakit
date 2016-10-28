# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from jubatus.weight.types import *

from .generic import GenericCLI
from ..args import Arguments, TDatum
from ..util import *
from ..._stdio import print

class WeightCLI(GenericCLI):
  @classmethod
  def _name(cls):
    return 'weight'

  @Arguments(TDatum)
  def do_update(self, d):
    """Syntax: update datum_key datum_value [...]
    Updates the model using the datum and calculates weights for it.
    """
    self._verbose("datum = {0}".format(d))
    for f in self.client.update(d):
      print('{0}\t{1}'.format(f.key, f.value))

  @Arguments(TDatum)
  def do_calc_weight(self, d):
    """Syntax: calc_weight datum_key datum_value [...]
    Calculates weights for the datum.
    """
    self._verbose("datum = {0}".format(d))
    for f in self.client.calc_weight(d):
      print('{0}\t{1}'.format(f.key, f.value))

