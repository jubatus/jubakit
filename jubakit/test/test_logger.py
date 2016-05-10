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
