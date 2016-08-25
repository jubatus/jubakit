# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.dumb import Burst
from jubakit._cli.service import BurstCLI

from .base import BaseCLITestCase

class BurstCLITest(BaseCLITestCase):
  def setUp(self):
    self._service = Burst.run(Burst.CONFIG)

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    self._ok([
      'clear',
      'add_keyword test',
      'add_document "test text"',
      'add_document "test text" 100',
      'get_result test',
      'get_result test 100',
      'get_all_bursted_results',
      'get_all_bursted_results 100',
      'get_all_keywords',
      'remove_keyword test',
      'remove_all_keywords',
      'add_keyword bar',
    ])
    keywords = map(lambda x: x.keyword, self._service._client().get_all_keywords())
    self.assertEqual(set(keywords), set(['bar']))

  def test_fail(self):
    self._fail([
      'add_keyword foo bar',
      'add_document',
      'add_documents',
      'get_result',
      'get_result test foo',
      'get_all_bursted_results foo',
      'get_all_keywords bar',
      'remove_all_keywords bar',
    ])
