# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

try:
  import numpy as np
  from scipy.sparse import csr_matrix
except ImportError:
  pass

from jubakit.loader.sparse import SparseMatrixLoader

from .. import requireSklearn

@requireSklearn
class SparseMatrixLoaderTest(TestCase):
  def _create_matrix(self):
    """
    Create a sparse matrix:

    [[1, 0, 2],
     [0, 0, 3],
     [4, 5, 6]]
    """
    row = np.array([0, 0, 1, 2, 2, 2])
    col = np.array([0, 2, 2, 0, 1, 2])
    data = np.array([1, 2, 3, 4, 5, 6])
    return csr_matrix((data, (row, col)), shape=(3, 3))

  def test_simple(self):
    loader = SparseMatrixLoader(
      self._create_matrix(),
      ['k1','k2','k3']
    )
    idx = 0
    for row in loader:
      if idx == 0:
        self.assertEqual(set(['k1', 'k3']), set(row.keys()))
        self.assertEqual(1, row['k1'])
        self.assertEqual(2, row['k3'])
      elif idx == 1:
        self.assertEqual(set(['k3']), set(row.keys()))
        self.assertEqual(3, row['k3'])
      elif idx == 2:
        self.assertEqual(set(['k1', 'k2', 'k3']), set(row.keys()))
        self.assertEqual(4, row['k1'])
        self.assertEqual(5, row['k2'])
        self.assertEqual(6, row['k3'])
      else:
        self.fail('unexpected row: {0}'.format(idx))
      idx += 1
