# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import time

from jubatus.burst.types import *

from .generic import GenericCLI
from ..args import Arguments, Optional
from ..util import *
from ..._stdio import print

class BurstCLI(GenericCLI):
  @classmethod
  def _name(cls):
    return 'burst'

  def _clear_cache(self):
    self._cached_keywords = set()

  def _print_window(self, kwd, w):
    print("Keyword: {0}".format(kwd))
    print("  Starting Position: {0}".format(w.start_pos))
    print("  Batches:")
    for bat in w.batches:
      print("  all_data_count = {0}, relevant_data_count = {1}, burst_weight = {2}".format(bat.all_data_count, bat.relevant_data_count, bat.burst_weight))

  @Arguments(str, Optional(float))
  def do_add_document(self, text, pos):
    """Syntax: add_document text [position]
    Adds a new document (text).
    When position is omitted, epoch time will be used.
    Bulk request (add_documents) is not supported on the command line.
    """
    if pos is None:
      pos = float(time.time())
    result = self.client.add_documents([Document(pos, text)])
    self._verbose("Position: {0}".format(pos))
    if result != 1:
      print("Failed; maybe the position is out-dated?")

  @Arguments(str, Optional(float))
  def do_get_result(self, keyword, pos):
    """Syntax: get_result keyword [position]
    Get the result of burst detection for the given keyword.
    When position is specified, get_result_at API will be called.
    Otherwise the latest result will be retrieved via get_result API.
    """
    if pos is None:
      result = self.client.get_result(keyword)
    else:
      result = self.client.get_result_at(keyword, pos)
    self._print_window(keyword, result)

  @Arguments(Optional(float))
  def do_get_all_bursted_results(self, pos):
    """Syntax: get_all_bursted_results keyword [position]
    Get the result of burst detection for all keywords.
    When position is specified, get_all_bursted_results_at API will be called.
    Otherwise the latest result will be retrieved via get_all_bursted_results API.
    """
    if pos is None:
      result = self.client.get_all_bursted_results()
    else:
      result = self.client.get_all_bursted_results_at(pos)
    for kwd in result:
      self._cached_keywords.add(kwd)
      self._print_window(kwd, result[kwd])

  @Arguments()
  def do_get_all_keywords(self):
    """Syntax get_all_keywords
    Prints all keywords and their parameters.
    """
    result = self.client.get_all_keywords()
    self._cached_keywords.clear()
    self._cached_keywords.update([x.keyword for x in result])
    for kwd in result:
      print("Keyword: {0}".format(kwd.keyword))
      print("  Scaling Parameter: {0}".format(kwd.scaling_param))
      print("  Gamma: {0}".format(kwd.gamma))

  @Arguments(str, Optional(float), Optional(float))
  def do_add_keyword(self, keyword, scaling_param, gamma):
    """Syntax: add_keyword keyword [scaling_param [gamma]]
    Adds the keyword for burst detection.
    scaling_param and gamma are optional; 2.0 and 1.0 is used when ommitted.
    """
    if scaling_param is None:
      scaling_param = 2.0
    if gamma is None:
      gamma = 1.0
    result = self.client.add_keyword(KeywordWithParams(keyword, scaling_param, gamma))
    self._cached_keywords.add(keyword)
    if not result:
      print("Failed; maybe the keyword is already registered?")

  @Arguments(str)
  def do_remove_keyword(self, keyword):
    """Syntax: remove_keyword keyword
    Removes the specified keyword.
    """
    result = self.client.remove_keyword(keyword)
    self._cached_keywords.discard(keyword)
    if not result:
      print("Failed; maybe the keyword does not exist on the server?")

  @Arguments()
  def do_remove_all_keywords(self):
    """Syntax: remove_all_keywords
    Removes all keywords.
    """
    result = self.client.remove_all_keywords()
    self._cached_keywords.clear()
    if not result:
      print("Failed")
