# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import shlex

from ..compat import builtins, shell_split

__all__ = [
  'print',
  'set_cli_output',
  'get_cli_output',
  'comp_position',
  'filter_candidates',
]

class _CLIOutput(object):
  _f = sys.stdout

def print(*args, **kwargs):
  """
  ``print`` method for CLI output.
  """
  builtins.print(file=_CLIOutput._f, *args, **kwargs)

def set_cli_output(f):
  _CLIOutput._f = f

def get_cli_output():
  return _CLIOutput._f

def comp_position(text, line, begidx, endidx):
  """
  Returns the current completion position of the argument.
  """
  return len(shell_split(line[:begidx])) - 1

def filter_candidates(text, candidates):
  """
  Filters completion candidates by the text being entered.
  """
  return [x for x in candidates if x.startswith(text)]
