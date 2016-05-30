# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from ..base import BaseLoader
from ..compat import *

class LineBasedStreamLoader(BaseLoader):
  """
  Loader to process line-oriented text stream.
  You can override `preprocess` method to separate the row into fields.
  """

  def __init__(self, f, close=False):
    self._f = f
    self._close = close
    self._lines = 0

  def rows(self):
    try:
      for line in self._f:
        yield {"number": self._lines, "line": line}
        self._lines += 1
    finally:
      if not self._f.closed and self._close:
        self._f.close()

class LineBasedFileLoader(LineBasedStreamLoader):
  """
  Loader to process line-oriented text file.
  """

  def __init__(self, filename, *args, **kwargs):
    f = open(filename, *args, **kwargs)
    super(LineBasedFileLoader, self).__init__(f, True)
