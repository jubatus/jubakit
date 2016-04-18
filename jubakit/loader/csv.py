# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import io

from ..base import BaseLoader
from ..compat import *

class CSVLoader(BaseLoader):
  """
  Loader to process CSV files.
  """

  def __init__(self, filename, fieldnames=None, encoding='utf-8', *args, **kwargs):
    """
    Creates a new loader that processes CSV files.

    You can optionally give `fieldnames` option.
    If `fieldnames` is not specified (which is a default) or specifeid as True,
    the first line of the CSV is used for column names.  If `fieldnames` is
    specified as False, sequential column names are automatically generated
    like ['c0', 'c1', ...].  If `fieldnames` is a list, it is used as column
    names.
    """

    if fieldnames == True:
      # Automatically estimate field names later.
      fieldnames = None
    elif fieldnames == False:
      # Generate field names by peeking number of columns in the first row
      # of the CSV.
      with io.open(filename, encoding=encoding, newline='') as f:
        for ent in csv.reader(f):
          fieldnames = ['c{0}'.format(i) for i in range(len(ent))]
          break

    self._filename = filename
    self._fieldnames = fieldnames
    self._encoding = encoding
    self._args = args
    self._kwargs = kwargs

  def __iter__(self):
    def _encode_file(f, enc):
      for line in f: yield line.encode(enc)
    def _decode_row(r, enc):
      return dict([(k.decode(enc), r[k].decode(enc)) for k in r.keys()])

    with io.open(self._filename, encoding=self._encoding, newline='') as f:
      f = f if PYTHON3 else _encode_file(f, self._encoding)
      reader = csv.DictReader(f, fieldnames=self._fieldnames, *self._args, **self._kwargs)
      for row in reader:
        ent = row if PYTHON3 else _decode_row(row, self._encoding)
        yield self.preprocess(ent)
