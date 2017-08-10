# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase
from tempfile import NamedTemporaryFile as TempFile
import json

import jubatus

from jubakit.model import \
    JubaDump, JubaModel, \
    InvalidModelFormatError, UnsupportedTransformationError, \
    _JubaModelCommand
from jubakit.compat import *
from jubakit._stdio import set_stdio, devnull

if PYTHON3:
  from io import StringIO, BytesIO
else:
  from StringIO import StringIO
  from io import BytesIO

# Ignore output from CLI classes
set_stdio(None, devnull(), devnull())

# Model data structure for test
TEST_JSON = {
  "header": {
    "format_version": 1,
    "jubatus_version_major": 1,
    "jubatus_version_minor": 2,
    "jubatus_version_maint": 3,
    "system_data_size": 0,
    "user_data_size": 0,
    "crc32": 0,  # invalid CRC32 checksum
  },
  "system": {
    "config": '{"method": "perceptron", "converter": {}}',
    "timestamp": 1500000000,
    "version": 1,
    "type": "classifier",
    "id": "foo",
  },
  "user": {
    "version": 1,
    "user_data": [[[{}, [{}, {}, 0]], [{}, {}, [0]]], [[0], [0, [{}], [{}], [{}], {}], [0, [{}], [{}], [{}], {}]]]
  },
  "user_raw": "kgGSkpKAk4CAAJOAgJEAk5EAlQCRgJGAkYCAlQCRgJGAkYCA",  # base64(msgpack.dumps(user_data))
}

def _get_model(valid=True):
  m = JubaModel.load_json(StringIO(json.dumps(TEST_JSON)))
  m.fix_header()
  if not valid:
    m.header.crc32 = 0  # break the model file
  return m

def _get_json_file(valid=True):
  f = StringIO()
  _get_model(valid).dump_json(f)
  f.seek(0)
  return f

def _get_binary_file(valid=True):
  f = BytesIO()
  _get_model(valid).dump_binary(f)
  f.seek(0)
  return f

class JubaDumpTest(TestCase):
  def test_simple(self):
    # Valid model must be dumped correctly.
    model = JubaDump.dump(_get_binary_file().read())
    self.assertTrue(isinstance(model, dict))

class JubaModelTest(TestCase):
  def test_binary(self):
    # get a valid binary model file
    f = _get_binary_file()

    # enable validation: must be loaded successfully
    m = JubaModel.load_binary(f, True)

    self.assertEqual(1, m.header.jubatus_version_major)
    self.assertEqual(2, m.header.jubatus_version_minor)
    self.assertEqual(3, m.header.jubatus_version_maint)
    self.assertNotEqual(1, m.header.crc32)  # must be a valid model after fix_header

    self.assertEqual(TEST_JSON['system']['config'], m.system.config)
    self.assertEqual('classifier', m.system.type)

    self.assertEqual(1, m.user.version)
    self.assertEqual(TEST_JSON['user']['user_data'], m.user.user_data)

    self.assertTrue(m._user_raw is not None)

  def test_binary_broken(self):
    # get a broken binary model file
    f = _get_binary_file(False)

    # enable validation: must detect an error
    self.assertRaises(InvalidModelFormatError, JubaModel.load_binary, f, True)

  def test_json(self):
    # get a valid JSON model file
    f = _get_json_file(True)

    # load it
    m = JubaModel.load_json(f)

    self.assertEqual(1, m.header.jubatus_version_major)
    self.assertEqual(2, m.header.jubatus_version_minor)
    self.assertEqual(3, m.header.jubatus_version_maint)

    self.assertNotEqual(0, m.header.crc32)

    self.assertEqual(TEST_JSON['system']['config'], m.system.config)
    self.assertEqual('classifier', m.system.type)
    self.assertEqual(1, m.user.version)
    self.assertEqual(TEST_JSON['user']['user_data'], m.user.user_data)
    self.assertTrue(m._user_raw is not None)

  def test_convert_matrix(self):
    for in_fmt in ('binary', 'json'):
      for out_fmt in ('binary', 'json', 'text'):
        # input
        if in_fmt == 'binary':
          m = JubaModel.load_binary(_get_binary_file())
        else:
          m = JubaModel.load_json(_get_json_file())

        # output
        if out_fmt == 'binary':
          f = BytesIO()
          m.dump_binary(f)
          f.seek(0)
          m2 = JubaModel.load_binary(f)
        elif out_fmt == 'json':
          f = StringIO()
          m.dump_json(f)
          f.seek(0)
          m2 = JubaModel.load_json(f)
        elif out_fmt == 'text':
          m.dump_text(StringIO())
          continue

        # check
        for ((k1, v1), (k2, v2)) in zip(m.header.get(), m2.header.get()):
          self.assertEqual(k1, k2)
          self.assertEqual(v1, v2)
        for ((k1, v1), (k2, v2)) in zip(m.user.get(), m2.user.get()):
          self.assertEqual(k1, k2)
          self.assertEqual(v1, v2)
        for ((k1, v1), (k2, v2)) in zip(m.system.get(), m2.system.get()):
          self.assertEqual(k1, k2)
          self.assertEqual(v1, v2)

  def test_transform(self):
    m1 = _get_model()  # classifier model
    m2 = m1.transform('weight')
    self.assertEqual('weight', m2.system.type)
    self.assertRaises(UnsupportedTransformationError, m2.transform, 'recommender')

class JubaModelCommandTest(TestCase):
  def _exit(self, args, status):
    return _JubaModelCommand.start(args)

  def test_help(self):
    args = ['--help']
    self.assertEqual(_JubaModelCommand.start(args), 0)

  def test_valid_param(self):
    with TempFile() as f:
      f.write(_get_binary_file().read())
      f.flush()
      args = ['--in-format', 'binary', '--out-format', 'json', f.name]
      self.assertEqual(_JubaModelCommand.start(args), 0)

  def test_invalid_param(self):
    with TempFile() as f:
      args = ['--in-format', 'none', f.name]
      self.assertNotEqual(_JubaModelCommand.start(args), 0)

      args = ['--out-format', 'none', f.name]
      self.assertNotEqual(_JubaModelCommand.start(args), 0)

      args = ['--no-such-option']
      self.assertNotEqual(_JubaModelCommand.start(args), 0)
