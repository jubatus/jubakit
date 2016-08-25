# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.classifier import Classifier, Config
from jubakit._cli.service import ClassifierCLI

from .base import BaseCLITestCase

class ClassifierCLITest(BaseCLITestCase):
  def setUp(self):
    self._service = Classifier.run(Config())

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    self._ok([
      'clear',
      'train pos x 1 y 1',
      'train neg x -1 y -1',
      'classify x 2 y 2',
      'set_label neutral',
      'get_labels',
      'delete_label pos',
    ])
    self.assertEqual(set(self._service._client().get_labels()), set(['neg', 'neutral']))

  def test_fail(self):
    self._fail([
      'train',
      'train pos x',
      'classify x',
      'set_label',
      'delete_label',
    ])

  def test_complete_train(self):
    cli = self._cli(ClassifierCLI, [
      'train pos x 1 y 1',
      'train neg x -1 y -1',
    ])
    candidates = cli.complete_train('', 'train ', 6, 6)
    self.assertEqual(set(candidates), set(['pos', 'neg']))
