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
    self._matrix = matrix
    self._feature_names = feature_names

  def __iter__(self):
    for row_mat in self._matrix:
      data = {}
      cols_idx = row_mat.nonzero()[1]
      feature_names = self._feature_names
      if feature_names is None:
        feature_names = ['v{0}'.format(i) for i in cols_idx]
      for i in cols_idx:
        data[feature_names[i]] = row_mat[0, i]
      yield self.preprocess(data)
