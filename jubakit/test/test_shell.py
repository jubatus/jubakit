# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

import jubatus

from jubakit.shell import JubaShell, JubashCommand
from jubakit._stdio import set_stdio, devnull

# Ignore output from CLI classes
set_stdio(None, devnull(), devnull())

class JubaShellTest(TestCase):
  def test_get_client_classes(self):
    classes = JubaShell.get_client_classes()
    self.assertTrue('generic' in classes)
    self.assertTrue('classifier' in classes)
    self.assertTrue('stat' in classes)

  def test_get_cli_classes(self):
    classes = JubaShell.get_cli_classes()
    self.assertTrue('generic' in classes)
    self.assertTrue('classifier' in classes)
    self.assertTrue('stat' in classes)

class JubashCommandTest(TestCase):
  def _assert_exit(self, args, status):
    self.assertEqual(JubashCommand.start(args), status)

  def test_help(self):
    args = ['--help']
    self._assert_exit(args, 0)

  def test_invalid_param(self):
    args = ['--port', '0']
    self._assert_exit(args, 1)

    args = ['--service', 'unknown']
    self._assert_exit(args, 1)

    args = ['--engine', 'unknown']
    self._assert_exit(args, 1)

    args = ['--no-such-option']
    self._assert_exit(args, 2)
