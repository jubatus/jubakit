# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

class BaseCLITestCase(TestCase):
  def __init__(self, *args, **kwargs):
    super(BaseCLITestCase, self).__init__(*args, **kwargs)

  def _shell(self, input=None):
    return self._service._shell(input=input)

  def _cli(self, clazz, pre_commands=[]):
    cli = clazz(self._shell())
    for cmd in pre_commands:
      cli.onecmd(cmd)
    return cli

  def _ok(self, commands):
    for cmd in commands:
      self.assertTrue(self._shell().run(cmd), cmd)

  def _fail(self, commands):
    for cmd in commands:
      self.assertFalse(self._shell().run(cmd), cmd)
