# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from jubatus.regression.types import *

from .generic import GenericCLI
from ..args import Arguments, TDatum
from ..util import *
from ..._stdio import print

class RegressionCLI(GenericCLI):
  @classmethod
  def _name(cls):
    return 'regression'

  @Arguments(float, TDatum)
  def do_train(self, score, d):
    """Syntax: train score datum_key datum_value [datum_key datum_value ...]
    Trains the model with given score and datum.
    Bulk training is not supported on the command line.
    """
    self._verbose("datum = {0}".format(d))
    result = self.client.train([ScoredDatum(score, d)])
    if result != 1:
      print("Failed")

  @Arguments(TDatum)
  def do_estimate(self, d):
    """Syntax: estimate datum_key datum_value [datum_key datum_value ...]
    Estimate the score for the given datum.
    Bulk estimation is not supported on the command line.
    """
    self._verbose("datum = {0}".format(d))
    result = self.client.estimate([d])[0]
    print(result)
