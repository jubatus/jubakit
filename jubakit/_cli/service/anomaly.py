# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from jubatus.anomaly.types import *

from .generic import GenericCLI
from ..args import Arguments, TDatum
from ..util import *
from ..._stdio import print

class AnomalyCLI(GenericCLI):
  @classmethod
  def _name(cls):
    return 'anomaly'

  @Arguments(str)
  def do_clear_row(self, row_id):
    """Syntax: clear_row row_id
    Clear the specified row.
    """
    result = self.client.clear_row(row_id)
    if not result:
      print("Failed")

  @Arguments(TDatum)
  def do_add(self, d):
    """Syntax: add datum_key datum_value [datum_key datum_value ...]
    Add a point.
    """
    self._verbose('datum = {0}'.format(d))
    point = self.client.add(d)
    print("Row ID: {0}".format(point.id))
    print("Score: {0}".format(point.score))

  @Arguments(str, TDatum)
  def do_update(self, row_id, d):
    """Syntax: update row_id datum_key datum_value [datum_key datum_value ...]
    Update a point.
    """
    self._verbose('datum = {0}'.format(d))
    score = self.client.update(row_id, d)
    print("Score: {0}".format(score))

  @Arguments(str, TDatum)
  def do_overwrite(self, row_id, d):
    """Syntax: overwrite row_id datum_key datum_value [datum_key datum_value ...]
    Overwrite the point.
    """
    self._verbose('datum = {0}'.format(d))
    score = self.client.overwrite(row_id, d)
    print("Score: {0}".format(score))

  @Arguments(TDatum)
  def do_calc_score(self, d):
    """Syntax: calc_score datum_key datum_value [datum_key datum_value ...]
    Calculate an anomaly measure value without adding a point.
    """
    self._verbose('datum = {0}'.format(d))
    score = self.client.calc_score(d)
    print("Score: {0}".format(score))

  @Arguments()
  def do_get_all_rows(self):
    """Syntax: get_all_rows
    Returns all rows. Note that converted rows will not be displayed.
    """
    rows = self.client.get_all_rows()
    for row in rows:
      print(row)
