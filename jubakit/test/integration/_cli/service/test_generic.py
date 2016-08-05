# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.classifier import Classifier, Config
from jubakit._cli.service import GenericCLI

from .base import BaseCLITestCase

class GenericCLITest(BaseCLITestCase):
  def setUp(self):
    self._service = Classifier.run(Config())
    self._sh = self._service._shell()

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    host = self._service._host
    port = self._service._port

    self._ok([
      'clear',
      'get_config',
      'save test',
      'load test',
      'get_status',
      # TODO consider distributed mode test
      #'get_proxy_status',
      #'do_mix',
      'connect {0} {1}'.format(host, port),
      'connect {0} {1} foo'.format(host, port),
      'reconnect',
      'verbose',
      'keepalive',
      'timeout',
      'timeout 10',
      'help',
      'exit',
    ])

  def test_fail(self):
    self._fail([
      'clear foo',
      'save',
      'load',
      'error',
      'verbose on',
      'timeout xx',
    ])

  def test_complete_command(self):
    cli = self._cli(GenericCLI)
    cli.complete('', 0)

    commands = set(cli.completion_matches)
    expected_commands = set(
      ['help', 'exit'] +
      ['connect', 'reconnect', 'verbose', 'keepalive', 'timeout'] +
      ['get_config', 'save', 'load', 'clear', 'get_status', 'get_proxy_status', 'do_mix']
    )
    self.assertEqual(commands, expected_commands)
