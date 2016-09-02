# -*- coding: utf-8 -*-

"""
Internal utilities.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os

from .compat import builtins

__all__ = [
  'print',
  'printe',
  'set_stdio',
  'get_stdio',
  'devnull',
]

class _StandardIO(object):
  """
  A class to override standard input/output/error.
  """

  _devnull = None

  stdin = sys.stdin
  stdout = sys.stdout
  stderr = sys.stderr

  @classmethod
  def get(cls):
    return (cls.stdin, cls.stdout, cls.stderr)

  @classmethod
  def set(cls, stdin=None, stdout=None, stderr=None):
    if stdin:  cls.stdin = stdin
    if stdout: cls.stdout = stdout
    if stderr: cls.stderr = stderr

  @classmethod
  def print(cls, *args, **kwargs):
    builtins.print(file=cls.stdout, *args, **kwargs)

  @classmethod
  def printe(cls, *args, **kwargs):
    builtins.print(file=cls.stderr, *args, **kwargs)

  @classmethod
  def devnull(cls):
    if cls._devnull is None:
      cls._devnull = open(os.devnull, 'w')
    return cls._devnull

print = _StandardIO.print
printe = _StandardIO.printe
set_stdio = _StandardIO.set
get_stdio = _StandardIO.get
devnull = _StandardIO.devnull
