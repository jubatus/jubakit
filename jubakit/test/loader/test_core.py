# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase
from io import StringIO
from tempfile import NamedTemporaryFile as TempFile

from jubakit.loader.core import LineBasedStreamLoader, LineBasedFileLoader

class LineBasedStreamLoaderTest(TestCase):
  def test_simple(self):
    data = 'hello\nworld'

    f = StringIO(data)
    loader = LineBasedStreamLoader(f, True)
    lines = []
    for line in loader:
      lines.append(line)

    self.assertEqual([{'line': 'hello\n'}, {'line': 'world'}], lines)

class LineBasedFileLoaderTest(TestCase):
  def test_simple(self):
    data = 'hello\nworld'
    lines = []

    with TempFile() as f:
      f.write(data.encode())
      f.flush()
      loader = LineBasedFileLoader(f.name)

      for line in loader:
        lines.append(line)

    self.assertEqual([{'line': 'hello\n'}, {'line': 'world'}], lines)
