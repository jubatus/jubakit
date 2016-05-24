# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase
from io import StringIO

from jubakit.logger import setup_logger, get_logger, INFO

class LoggerTest(TestCase):
  MESSAGE = 'this is log'

  def test_simple(self):
    buf = StringIO()
    setup_logger(level=INFO, f=buf)
    get_logger().info(self.MESSAGE)
    buf.seek(0)
    msg = buf.read()
    self.assertTrue(self.MESSAGE in msg)

  def test_child(self):
    buf = StringIO()
    setup_logger(level=INFO, f=buf)
    get_logger('child').info(self.MESSAGE)
    buf.seek(0)
    msg = buf.read()
    self.assertTrue(self.MESSAGE in msg)
    self.assertTrue('jubakit.child' in msg)
