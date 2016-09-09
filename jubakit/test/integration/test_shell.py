# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from io import StringIO

from jubakit.shell import JubaShell, JubashCommand
from jubakit.classifier import Classifier, Config

class JubaShellTest(TestCase):
  def setUp(self):
    self._service = Classifier.run(Config())

  def tearDown(self):
    self._service.stop()

  def _shell(self, cmd='', service_name=None):
    s = self._service
    if not service_name:
      service_name = s.name()
    shell = JubaShell(
      s._host,
      s._port,
      s._cluster,
      service_name,
      input=StringIO(cmd),
    )
    return shell

  def test_interact(self):
    self.assertTrue(self._shell('classify x 1').interact())
    self.assertTrue(self._shell('error').interact())
    self.assertTrue(self._shell('connect 127.0.0.1 0').interact())
    self.assertTrue(self._shell('! echo OK').interact())

    # Interface mismatch (using anomaly shell against classifier service)
    self.assertFalse(self._shell('calc_score x 1', 'anomaly').interact())

  def test_run(self):
    self.assertTrue(self._shell().run('classify x 1'))
    self.assertFalse(self._shell().run('error'))
    self.assertFalse(self._shell().run('connect 127.0.0.1 0'))
    self.assertFalse(self._shell().run('connect 127.0.0.1 -1'))
    self.assertFalse(self._shell().run('connect this_must_be_unknown_host 9199'))
    self.assertFalse(self._shell('', 'anomaly').run('calc_score x 1'))

class JubashCommandTest(TestCase):
  def setUp(self):
    self._service = Classifier.run(Config())

  def tearDown(self):
    self._service.stop()

  def _assert_exit(self, args, status):
    self.assertEqual(JubashCommand.start(args), status)

  def test_simple(self):
    args = [
      '--host', self._service._host,
      '--port', str(self._service._port),
      '--service', self._service.name(),
      '--command', 'classify x 1',
    ]
    self._assert_exit(args, 0)

  def test_service_estimate(self):
    args = [
      '--host', self._service._host,
      '--port', str(self._service._port),
      '--command', 'classify x 1',
    ]
    self._assert_exit(args, 0)
