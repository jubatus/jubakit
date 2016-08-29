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

    Any other optional or keyword arguments are passed to the underlying
    `csv.DictReader`.

    >>> loader = CSVLoader('dataset.tsv', fieldnames=False, encoding='cp932', delimiter='\t')
    """

    if fieldnames == True:
      # Automatically estimate field names later.
      fieldnames = None
    elif fieldnames == False:
      # Generate field names by peeking number of columns in the first row of the CSV.
      with io.open(filename, encoding=encoding, newline='') as f:
        # Use fieldnames from DictReader to count number of columns in the first row.
        r = _UnicodeDictReader(f, encoding, fieldnames=None, *args, **kwargs)
        fieldnames = ['c{0}'.format(i) for i in range(len(r.fieldnames))]

    self._filename = filename
    self._fieldnames = fieldnames
    self._encoding = encoding
    self._args = args
    self._kwargs = kwargs

  def rows(self):
    with io.open(self._filename, encoding=self._encoding, newline='') as f:
      reader = _UnicodeDictReader(f, self._encoding, fieldnames=self._fieldnames, *self._args, **self._kwargs)
      for row in reader:
        yield row

class _UnicodeDictReader(csv.DictReader):
  def __init__(self, f, encoding, *args, **kwargs):
    self._encoding = encoding

    # DictReader in Python 2.x use str (bytes) for parameters, whereas Python 3.x use
    # str (unicode) for them.  The code below is intended to absorbs the difference.
    def convert(v):
      if PYTHON3 and isinstance(v, bytes):
        return v.decode(encoding)
      elif not PYTHON3 and isinstance(v, unicode_t):
        return v.encode(encoding)
      return v

    for k in ['delimiter', 'escapechar', 'quotechar', 'lineterminator', 'restkey', 'restval']:
      if k in kwargs: kwargs[k] = convert(kwargs[k])

    fieldnames = kwargs.get('fieldnames', None)
    if fieldnames:
      kwargs['fieldnames'] = list(map(lambda x: convert(x), fieldnames))

    # DictReader in Python 2.x cannot handle Unicode input.
    # We transcode each line of CSV row into bytes for Py2.
    def encode_file(f):
      for line in f:
        yield line.encode(encoding)
    f = f if PYTHON3 else encode_file(f)
    csv.DictReader.__init__(self, f, *args, **kwargs)

  def next(self):
    r = csv.DictReader.next(self)
    if PYTHON3:
      return r
    else:
      # DictReader in Python 2.x returns rows in bytes.  We transcode keys/values of
      # the row dict into Unicode like in Python 3.x.
      return dict([(k.decode(self._encoding), r[k].decode(self._encoding)) for k in r.keys()])
