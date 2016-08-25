# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.dumb import Clustering
from jubakit._cli.service import ClusteringCLI

from .base import BaseCLITestCase

class ClusteringCLITest(BaseCLITestCase):
  def setUp(self):
    cfg = Clustering.CONFIG
    cfg['parameter']['bucket_size'] = 3
    cfg['parameter']['compressed_bucket_size'] = 2
    cfg['parameter']['bicriteria_base_size'] = 1
    self._service = Clustering.run(cfg)

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    self._ok([
      'clear',
      'push x 1 y 1',
      'push x 1 y 2',
      'push x 1 y 3',
      'push x 5 y 1',
      'push x 5 y 2',
      'push x 5 y 3',
      'get_revision',
      'get_k_center',
      'get_nearest_center x 1 y 1',
      'get_nearest_members x 5 y 5',
      'get_core_members',
    ])
    self.assertEqual(self._service._client().get_revision(), 2)

  def test_fail(self):
    self._fail([
      'push x',
      'get_revision foo',
      'get_k_center foo',
      'get_nearest_center x 1 y',
      'get_nearest_members x',
      'get_core_members foo',
    ])
