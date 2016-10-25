# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os
import logging

# Import log levels.
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

# Define the default logging format.
_DEFAULT_FORMAT = '[%(name)s] %(asctime)s: (%(levelname)s) %(message)s'

# jubakit root logger name.
_LOGGER_NAME = 'jubakit'

class _Logger(object):
  # Logger instance.
  logger = None

  # Define the defualt log handler which does nothing.
  class _NullHandler(logging.Handler):
    def emit(self, record):
      pass

  @classmethod
  def init(cls):
    cls.logger = logging.getLogger(_LOGGER_NAME)
    logger = cls.logger
    levelname = os.environ.get('JUBAKIT_LOG_LEVEL', None)
    if not levelname:
      # Surpress printing logs by default.
      logger.addHandler(cls._NullHandler())
      logger.setLevel(CRITICAL)
      return

    # Setup logger from environment variable.
    for lvl in (DEBUG, INFO, WARNING, ERROR, CRITICAL):
      if logging.getLevelName(lvl) == levelname:
        setup_logger(lvl)
        break
    else:
      setup_logger(INFO)
      logger.warning('invalid JUBAKIT_LOG_LEVEL (%s) specified; continue with INFO', levelname)

def setup_logger(level=WARNING, f=sys.stderr, log_format=_DEFAULT_FORMAT):
  """
  Convenient method to setup the logger.
  """
  handler = logging.StreamHandler(f)
  handler.setFormatter(logging.Formatter(log_format))

  logger = _Logger.logger
  logger.propagate = False
  logger.addHandler(handler)
  logger.setLevel(level)

def get_logger(name=None):
  """
  Returns the logger.
  If `name` is specified, child logger is returned.
  Otherwise the default jubakit logger is returned.

  This is mainly expected for internal uses but users can get logger
  to print their own logs.
  """
  logger = _Logger.logger
  if name is None:
    return logger
  elif hasattr(logger, 'getChild'):  # Python 2.7+
    return logger.getChild(name)
  else:
    return logging.getLogger('{0}.{1}'.format(_LOGGER_NAME, name))
