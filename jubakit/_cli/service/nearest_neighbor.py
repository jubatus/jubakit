# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from jubatus.nearest_neighbor.types import *

from .generic import GenericCLI
from ..args import Arguments, Optional, TDatum
from ..util import *
from ..._stdio import print

class NearestNeighborCLI(GenericCLI):
  @classmethod
  def _name(cls):
    return 'nearest_neighbor'

  def _clear_cache(self):
    self._max_results = 100

  def _print_id_with_scores(self, result):
    for ent in result:
      print("{0:<15} {1:>}".format(ent.score, ent.id))

  @Arguments(str, TDatum)
  def do_set_row(self, row_id, d):
    """Syntax: set_row row_id datum_key datum_value [...]
    Updates the row whose id is row_id with given datum.
    """
    self._verbose("datum = {0}".format(d))
    result = self.client.set_row(row_id, d)
    if not result:
      print("Failed")

  @Arguments(str)
  def do_neighbor_row_from_id(self, row_id):
    """Syntax: neighbor_row_from_id row_id
    Get rows that have most similar datum to the given row ID.
    """
    result = self.client.neighbor_row_from_id(row_id, self._max_results)
    self._print_id_with_scores(result)

  @Arguments(TDatum)
  def do_neighbor_row_from_datum(self, d):
    """Syntax: neighbor_row_from_datum datum_key datum_value [...]
    Get rows that have most similar datum to the given datum.
    """
    self._verbose("datum = {0}".format(d))
    result = self.client.neighbor_row_from_datum(d, self._max_results)
    self._print_id_with_scores(result)

  @Arguments(str)
  def do_similar_row_from_id(self, row_id):
    """Syntax: similar_row_from_id row_id
    Get rows that have most similar datum to the given row ID.
    """
    result = self.client.similar_row_from_id(row_id, self._max_results)
    self._print_id_with_scores(result)

  @Arguments(TDatum)
  def do_similar_row_from_datum(self, d):
    """Syntax: similar_row_from_datum datum_key datum_value [...]
    Get rows that have most similar datum to the given datum.
    """
    self._verbose("datum = {0}".format(d))
    result = self.client.similar_row_from_datum(d, self._max_results)
    self._print_id_with_scores(result)

  @Arguments()
  def do_get_all_rows(self):
    """Syntax: get_all_rows
    Returns all rows. Note that converted rows will not be displayed.
    """
    rows = self.client.get_all_rows()
    for row in rows:
      print(row)

  @Arguments(Optional(int))
  def do_max_results(self, new_value):
    """Syntax: max_results [new_value]
    Displays or changes the maximum number of results for {neighbor,similar}_row_from_{id,data}.
    """
    if new_value is None:
      print(self._max_results)
    else:
      self._max_results = new_value
