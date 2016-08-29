# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import cmd

class ExtendedCmd(cmd.Cmd, object):
  """
  Extended framework of standard cmd.Cmd class with better completion
  support and alias features.
  """

  def parseline(self, line):
    line = line.strip()
    if not line:
      return None, None, line
    elif line[0] == '?':
      line = 'help ' + line[1:]
    elif line[0] == '!':
      if hasattr(self, 'do_shell'):
        line = 'shell ' + line[1:]
      else:
        return None, None, line
    i, n = 0, len(line)
    while i < n and line[i] in self.identchars: i = i+1
    cmd, arg = line[:i], line[i:].strip()
    return cmd, arg, line

  def complete(self, text, state):
    result = super(ExtendedCmd, self).complete(text, state)
    if len(self.completion_matches) == 1:
      return self.completion_matches[state] + ' ' if state == 0 else None
    return result

  def register_alias(self, alias, name):
    """
    Register alias function to the method.
    Aliases are not listed by `help` command.
    """
    self.__dict__['do_' + alias] = getattr(self, name)
