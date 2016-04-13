# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from ..base import BaseLoader
from ..compat import *

class SparseMatrixLoader(BaseLoader):
  """
  SparseMatrixLoader is a loader to read from scipy.sparse 2-d matrix.
  Zero entries are ignored.
  """

  def __init__(self, matrix, feature_names=None):
    self._matrix = matrix.tocsr()
    self._feature_names = feature_names

  def __iter__(self):
    m = self._matrix
    for i in range(m.shape[0]):
      cols = m.indices[m.indptr[i]:m.indptr[i+1]]

      if self._feature_names is None:
        fv_names = ['v{0}'.format(col) for col in cols]
      else:
        fv_names = [self._feature_names[col] for col in cols]

      data = dict(zip(fv_names, m.data[m.indptr[i]:m.indptr[i+1]]))
      yield self.preprocess(data)
