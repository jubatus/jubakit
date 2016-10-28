# -*- coding: utf-8 -*-

"""
Classes for command line argument type validation.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import inspect

from jubatus.common import Datum

from .util import shell_split

class Rule(object):
  def convert(self, args):
    raise NotImplementedError

  def min_max(self):
    raise NotImplementedError

class Type(Rule): pass

class Requirement(Rule): pass

class Mandatory(Requirement):
  def __init__(self, t):
    self.t = t

  def convert(self, args):
    if issubclass(self.t, Type):
      return self.t().convert(args)
    else:
      return (1, self.t(args[0]))

  def min_max(self):
    if issubclass(self.t, Type):
      return self.t().min_max()
    else:
      return (1, 1)

class Optional(Mandatory):
  def convert(self, args):
    if len(args) == 0:
      return (0, None)
    return super(Optional, self).convert(args)

  def min_max(self):
    return (0, super(Optional, self).min_max()[1])

def Arguments(*expected_types):
  def wrap_by_preprocessor(func):
    assert len(inspect.getargspec(func).args) == (len(expected_types) + 1)

    def preprocessor(self, line):
      params = shell_split(line)
      types = []
      (min_count, max_count) = (0, 0)

      for t in expected_types:
        if not isinstance(t, Requirement):
          t = Mandatory(t)
        types.append(t)
        (t_min, t_max) = t.min_max()
        min_count += t_min
        if t_max is None:
          max_count = None
        elif max_count is not None:
          max_count += t_max

      params_len = len(params)
      if params_len < min_count:
        raise ValueError('Too few arguments ({0} required at least, only got {1})'.format(min_count, params_len))
      if max_count is not None and max_count < params_len:
        raise ValueError('Too many arguments ({0} required at most, got {1})'.format(max_count, params_len))

      index = 0
      argv = []
      for t in types:
        try:
          (consumed, value) = t.convert(params[index:])
        except ValueError as e:
          raise ValueError('argument {0}: {1}'.format(index + 1, e))
        argv.append(value)
        index += consumed
      return func(self, *argv)
    preprocessor.__doc__ = func.__doc__
    return preprocessor
  return wrap_by_preprocessor

class TProperty(Type):
  def convert(self, args):
    if len(args)  % 2 != 0:
      raise ValueError('value for the last property key ({0}) is missing'.format(args[len(args) - 1]))
    p = {}
    for i in range(int(len(args) / 2)):
      p[args[i*2]] = args[i*2+1]
    return (len(args), p)

  def min_max(self):
    return (2, None)

class TDatum(Type):
  def convert(self, args):
    if len(args) % 2 != 0:
      raise ValueError('value for the last datum key ({0}) is missing'.format(args[len(args) - 1]))

    d = Datum()
    for i in range(int(len(args) / 2)):
      feat_key = args[i*2]
      feat_val = args[i*2+1]
      try:
        d.add_number(feat_key, float(feat_val))
      except ValueError:
        d.add_string(feat_key, feat_val)
    return (len(args), d)

  def min_max(self):
    return (0, None)

def TMultiDatum(count):
  class TOffsetDatum(TDatum):
    def convert(self, args):
      if '|' not in args:
        raise ValueError('insufficient number of datum')
      (consumed, value) = super(TOffsetDatum, self).convert(args[:args.index('|')])
      return (consumed + 1, value)

    def min_max(self):
      return (1, None)

  return [TOffsetDatum] * (count - 1) + [TDatum]
