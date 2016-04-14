# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import codecs

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
      with open(filename, 'r') as f:
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
      return dict(map(lambda (k, v): (k.decode(enc), v.decode(enc)), r.items()))

    with codecs.open(self._filename, 'r', self._encoding) as f:
      reader = csv.DictReader(_encode_file(f, self._encoding), self._fieldnames, *self._args, **self._kwargs)
      for row in reader:
        yield self.preprocess(_decode_row(row, self._encoding))
