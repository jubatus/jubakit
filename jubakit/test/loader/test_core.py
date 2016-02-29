# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from StringIO import StringIO
from jubakit.loader.core import BasicLineBasedStreamLoader, BasicLineBasedFileLoader

class BasicLineBasedStreamLoaderTest(TestCase):
  def test_simple(self):
    data = 'hello\nworld'

    f = StringIO(data)
    loader = BasicLineBasedStreamLoader(f, True)
    lines = []
    for line in loader:
      lines.append(line)

    self.assertEqual([{'line': u'hello\n'}, {'line': u'world'}], lines)
