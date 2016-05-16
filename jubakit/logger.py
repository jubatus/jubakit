# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import logging

# Import log levels.
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

# Define the default logging format.
_DEFAULT_FORMAT = '[%(name)s] %(asctime)s: (%(levelname)s) %(message)s'

# Define the defualt logger which does nothing.
class _NullHandler(logging.Handler):
  def emit(self, record):
    pass

_logger = logging.getLogger('jubakit')
_logger.addHandler(_NullHandler())
_logger.setLevel(logging.CRITICAL)

def setup_logger(level=logging.WARNING, f=sys.stderr, log_format=_DEFAULT_FORMAT):
  """
  Convenient method to setup the logger.
  """
  handler = logging.StreamHandler(f)
  handler.setFormatter(logging.Formatter(log_format))

  _logger.propagate = False
  _logger.addHandler(handler)
  _logger.setLevel(level)

def get_logger(name=None):
  """
  Returns the logger.
  If `name` is specified, child logger is returned.
  Otherwise the default jubakit logger is returned.

  This is mainly expected for internal uses but users can get logger
  to print their own logs.
  """
  if name is None:
    return _logger
  return _logger.getChild(name)
