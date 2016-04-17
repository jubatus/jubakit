# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from io import StringIO
from jubakit.loader.core import LineBasedStreamLoader, LineBasedFileLoader

class LineBasedStreamLoaderTest(TestCase):
  def test_simple(self):
    data = 'hello\nworld'

    f = StringIO(data)
    loader = LineBasedStreamLoader(f, True)
    lines = []
    for line in loader:
      lines.append(line)

    self.assertEqual([{'line': u'hello\n'}, {'line': u'world'}], lines)
