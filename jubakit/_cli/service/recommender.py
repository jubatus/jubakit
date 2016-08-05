# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from jubatus.recommender.types import *

from .generic import GenericCLI
from ..args import Arguments, Optional, TDatum, TMultiDatum
from ..util import *

class RecommenderCLI(GenericCLI):
  @classmethod
  def _name(cls):
    return 'recommender'

  def _clear_cache(self):
    self._max_results = 100

  def _print_similar_result(self, results):
    results.sort(key=lambda e: e.score, reverse=True)
    for result in results:
      print("{0}: {1}".format(result.id, result.score))

  @Arguments(str)
  def do_clear_row(self, row_id):
    """Syntax: clear_row row_id
    Clear the specified row.
    """
    result = self.client.clear_row(row_id)
    if not result:
      print("Failed")

  @Arguments(str, TDatum)
  def do_update_row(self, row_id, d):
    """Syntax: update_row row_id datum_key datum_value [datum_key datum_value ...]
    Update or insert a new row.
    """
    self._verbose("datum = {0}".format(d))
    result = self.client.update_row(row_id, d)
    if not result:
      print("Failed")

  @Arguments(str)
  def do_complete_row_from_id(self, row_id):
    """Syntax: complete_row_from_id id
    Complete row from the given ID.
    """
    d = self.client.complete_row_from_id(row_id)
    print(d)

  @Arguments(TDatum)
  def do_complete_row_from_datum(self, d):
    """syntax: complete_row_from_datum datum_key datum_value [datum_key datum_value ...]
    Complete row from the given datum.
    """
    self._verbose("datum = {0}".format(d))
    d = self.client.complete_row_from_datum(d)
    print(d)

  @Arguments(str)
  def do_similar_row_from_id(self, row_id):
    """Syntax: similar_row_from_id id
    Similar row from the given ID.
    """
    results = self.client.similar_row_from_id(row_id, self._max_results)
    self._print_similar_result(results)

  @Arguments(TDatum)
  def do_similar_row_from_datum(self, d):
    """syntax: similar_row_from_datum datum_key datum_value [datum_key datum_value ...]
    Similar row from the given datum.
    """
    results = self.client.similar_row_from_datum(d, self._max_results)
    self._print_similar_result(results)

  @Arguments(str)
  def do_decode_row(self, row_id):
    """Syntax: decode_row id
    Decode the row of given ID.
    """
    d = self.client.decode_row(row_id)
    print(d)

  @Arguments()
  def do_get_all_rows(self):
    """Syntax: get_all_rows
    Returns all rows. Note that converted rows will not be displayed.
    """
    rows = self.client.get_all_rows()
    for row in rows:
      print(row)

  @Arguments(*TMultiDatum(2))
  def do_calc_similarity(self, lhs, rhs):
    """Syntax: calc_similarity datum1_key datum1_value ... | datum2_key datum2_value ...
    Calculates similarity between two datum.
    Separate two datum records with a bar ('|').
    """
    self._verbose("datum(lhs) = {0}".format(lhs))
    self._verbose("datum(rhs) = {0}".format(rhs))
    similarity = self.client.calc_similarity(lhs, rhs)
    print(similarity)

  @Arguments(TDatum)
  def do_calc_l2norm(self, d):
    """Syntax: calc_l2norm datum_key datum_value ...
    Calculates L2 norm for the given datum.
    """
    self._verbose("datum = {0}".format(d))
    l2norm = self.client.calc_l2norm(d)
    print(l2norm)

  @Arguments(Optional(int))
  def do_max_results(self, new_value):
    """Syntax: max_results [new_value]
    Displays or changes the maximum number of results for similar_row_from_{id,datum}.
    """
    if new_value is None:
      print(self._max_results)
    else:
      self._max_results = new_value
