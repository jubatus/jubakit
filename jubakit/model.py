# -*- coding: utf-8 -*-

"""
This module provides features to manipulate model files.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import copy
import struct
from binascii import crc32
from io import BytesIO
import base64
import subprocess
import tempfile
import optparse

import msgpack
import json

from .compat import *
from ._stdio import print, printe, get_stdio
from ._process import JubaProcess

class JubaDump(object):
  """
  ``JubaDump`` provides a high-level dump of Jubatus models.
  ``jubadump`` command must be installed.
  """

  @classmethod
  def dump_file(cls, target):
    """
    Returns the dumped model data structure of the model file path ``target``.
    """
    proc = JubaProcess.get_process(['jubadump', '-i', target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = proc.communicate()
    status = proc.returncode
    if status != 0:
      raise InvalidModelFormatError('{0} (exit with status {1})'.format(stderr, status))
    return json.loads(stdout.decode())

  @classmethod
  def dump(cls, data):
    """
    Returns the dumped model data structure of the raw model data.
    """
    with tempfile.NamedTemporaryFile(mode='wb', prefix='jubakit-jubadump-') as f:
      f.write(data)
      f.flush()
      return cls.dump_file(f.name)

class JubaModel(object):
  """
  ``JubaModel`` provides features to perform low-level manipulation of Jubatus model data structure.
  """

  def __init__(self):
    self.header = self.Header()
    self.system = self.SystemContainer()
    self.user = self.UserContainer()
    self._user_raw = None

  @classmethod
  def load_binary(cls, f, validate=True):
    """
    Loads Jubatus binary model file from binary stream ``f``.
    When ``validate`` is ``True``, the model file format is strictly validated.
    """
    m = cls()
    checksum = 0

    # Load header
    h = cls.Header.load(f)
    m.header = h
    if validate:
      checksum = crc32(h.dumps(False), checksum)

    # Load system_data
    buf = f.read(h.system_data_size)
    m.system = cls.SystemContainer.loads(buf)
    if validate:
      if h.system_data_size != len(buf):
        raise InvalidModelFormatError(
          'EOF detected while reading system_data: ' +
          'expected {0} bytes, got {1} bytes'.format(h.system_data_size, len(buf)))
      checksum = crc32(buf, checksum)

    # Load user_data
    buf = f.read(h.user_data_size)
    m.user = cls.UserContainer.loads(buf)
    m._user_raw = buf
    if validate:
      if h.user_data_size != len(buf):
        raise InvalidModelFormatError(
          'EOF detected while reading user_data: ' +
          'expected {0} bytes, got {1} bytes'.format(h.user_data_size, len(buf)))
      checksum = crc32(buf, checksum)

    if validate:
      # Convert the checksum into 32-bit unsigned integer (for Python 2/3 compatibility)
      checksum = checksum & 0xffffffff

      # Check CRC
      if checksum != h.crc32:
        raise InvalidModelFormatError(
          'CRC32 mismatch: expected {0}, got {1}'.format(checksum, h.crc32))
    return m

  def dump_binary(self, f):
    """
    Dumps the model as Jubatus binary model file to binary stream ``f``.
    """
    # Dump header
    self.header.dump(f)

    # Dump system_data
    self.system.dump(f)

    # Dump user_data
    if self._user_raw is None:
      printe('Warning: conversion from Python object to binary model format may generate corrupt model')
      self.user.dump(f)
    else:
      f.write(self._user_raw)

  @classmethod
  def load_json(cls, f):
    """
    Loads model file saved as JSON file from text stream ``f``.
    """
    m = cls()
    record = json.load(f)

    # Load header
    if 'header' not in record:
      raise InvalidModelFormatError('header section does not exist')
    m.header.set(record['header'])

    # Load system_data
    if 'system' not in record:
      raise InvalidModelFormatError('system section does not exist')
    m.system.set(record['system'])

    # Load user_data
    if 'user_raw' in record:
      if 'user' in record:
        printe('Notice: using "user_raw" record from JSON; "user" record is ignored')
      raw = base64.b64decode(record['user_raw'])
      try:
        m.user = cls.UserContainer.loads(raw)
      except UnicodeDecodeError:
        printe('Warning: model contains non UTF-8 strings; cannot be loaded')
        m.user = cls.UserContainer()
        m.user.user_data = None
      m._user_raw = raw
    elif 'user' in record:
      m.user.set(record['user'])
    else:
      raise InvalidModelFormatError('user or user_raw section does not exist')

    return m

  def dump_json(self, f, without_raw=False):
    """
    Dumps the model as JSON file to a text stream ``f``.
    """
    record = {}

    # Dump header
    record['header'] = dict(self.header.get())

    # Dump system_data
    record['system'] = dict(self.system.get())

    # Dump user_data
    record['user'] = dict(self.user.get())
    if not without_raw:
      record['user_raw'] = base64.b64encode(self._user_raw).decode()

    json.dump(record, f, indent=2)

  def dump_text(self, f):
    """
    Dumps the model as human-readable text format to a text stream ``f``.
    """
    buf = []
    for (heading, obj) in [ ('Meta Data',   self.header),
                            ('System Data', self.system),
                            ('User Data',   self.user) ]:
      buf.append("------------------------------------------")
      buf.append(heading)
      buf.append("------------------------------------------")

      for (k, v) in obj.get():
        buf.append('{0:24}{1}'.format(k, v))
      buf.append('')
    f.write('\n'.join(buf))

  @classmethod
  def predict_format(cls, filename):
    """
    Loads the model file named ``filename``.
    Returns ``binary`` or ``json``.
    """
    with open(filename, 'rb') as f:
      sig = f.read(1)
      f.seek(-1, 1)
      if sig[0] == cls.Header._MAGIC[0]:
        return 'binary'
      elif sig == b'{':
        return 'json'
    raise InvalidModelFormatError('model format cannot be predicted')

  def fix_header(self):
    """
    Repairs the header values.
    """
    # Update magic
    self.header.magic = self.header._MAGIC

    # Update system_data_size
    system_raw = self.system.dumps()
    self.header.system_data_size = len(system_raw)

    # Update user_data_size
    user_raw = self._user_raw
    self.header.user_data_size = len(user_raw)

    # Update crc32
    header_raw = self.header.dumps(False)
    checksum = 0
    checksum = crc32(header_raw, checksum)
    checksum = crc32(system_raw, checksum)
    checksum = crc32(user_raw, checksum)

    # Convert the checksum into 32-bit unsigned integer (for Python 2/3 compatibility)
    self.header.crc32 = (checksum & 0xffffffff)

  def data(self):
    """
    Returns the actual model data part.
    This method is a quick shortcut for ``return self.user.user_data``.
    """
    return self.user.user_data

  def transform(self, service):
    t = self.system.type
    trans = None
    if t == 'classifier':
      trans = ClassifierTransformer(self)
    elif t == 'regression':
      trans = RegressionTransformer(self)
    elif t == 'recommender':
      trans = RecommenderTransformer(self)
    elif t == 'anomaly':
      trans = AnomalyTransformer(self)
    elif t == 'clustering':
      trans = ClusteringTransformer(self)
    else:
      raise UnsupportedTransformationError(t)
    return trans.transform(service)

  class ModelPart(object):
    def __init__(self):
      for (key, _, default) in self.fields():
        setattr(self, key, default)

    @classmethod
    def fields(cls):
      """
      Returns the list of (property_name, data_type, default_value).
      """
      raise NotImplementedError

    def get(self):
      record = []
      for (key, _, _) in self.fields():
        record.append((key, getattr(self, key),))
      return record

    def set(self, record):
      for (key, _, _) in self.fields():
        new_value = record[key]
        if isinstance(new_value, bytes):
          new_value = new_value.decode()
        setattr(self, key, new_value)

    @classmethod
    def load(cls, f, *args, **kwargs):
      # Must be implemented in sub classes.
      raise NotImplementedError

    @classmethod
    def loads(cls, data, *args, **kwargs):
      return cls.load(BytesIO(data), *args, **kwargs)

    def dump(self, f, *args, **kwargs):
      # Must be implemented in sub classes.
      raise NotImplementedError

    def dumps(self, *args, **kwargs):
      f = BytesIO()
      self.dump(f, *args, **kwargs)
      return f.getvalue()

  class Header(ModelPart):
    # Magic value for binary model files.
    _MAGIC = b'jubatus\0'

    @classmethod
    def fields(cls):
      return [
        ('format_version'       , b'>Q', 1),
        ('jubatus_version_major', b'>I', 0),
        ('jubatus_version_minor', b'>I', 0),
        ('jubatus_version_maint', b'>I', 0),
        ('crc32'                , b'>I', 0),
        ('system_data_size'     , b'>Q', 0),
        ('user_data_size'       , b'>Q', 0),
      ]

    @classmethod
    def load(cls, f):
      h = cls()

      magic = f.read(8)
      if len(magic) != 8 or magic != cls._MAGIC:
        raise InvalidModelFormatError('invalid magic value: {0}'.format(str(magic)))

      for (key, fmt, _) in cls.fields():
        size = struct.calcsize(fmt)
        raw = f.read(size)
        if len(raw) != size:
          raise InvalidModelFormatError('failed to read {0} in header (expected {1} bytes, got {2} bytes)'.format(key, size, len(raw)))
        try:
          value = struct.unpack(fmt, raw)[0]
        except ValueError:
          raise InvalidModelFormatError('failed to parse {0} value {1} as {2}'.format(key, str(raw), fmt))
        setattr(h, key, value)
      return h

    def dump(self, f, checksum=True):
      f.write(bytes(self._MAGIC))
      for (key, fmt, _) in self.fields():
        if key == 'crc32' and not checksum: continue  # skip checksum if checksum == False
        f.write(struct.pack(fmt, getattr(self, key)))

  class Container(ModelPart):
    @classmethod
    def load(cls, f):
      # Assumes everything is encoded in UTF-8.
      # This means that if some records (e.g., config files, feature vector
      # keys) are not encoded in UTF-8, the model cannot be loaded.  However,
      # such models cannot be written out to text or JSON, so we don't really
      # care.  Callers are responsible for handling UnicodeDecodeError.
      values = msgpack.load(f, encoding='utf-8', unicode_errors='strict')
      field_names = map(lambda x: x[0], cls.fields())
      c = cls()
      c.set(dict(zip(field_names, values)))
      return c

    def dump(self, f):
      values = list(map(lambda x: x[1], self.get()))
      msgpack.dump(values, f)

  class SystemContainer(Container):
    @classmethod
    def fields(cls):
      return [
        ('version'  , int  , 0),
        ('timestamp', int  , 0),
        ('type'     , bytes, b''),
        ('id'       , bytes, b''),
        ('config'   , bytes, b''),
      ]

  class UserContainer(Container):
    @classmethod
    def fields(cls):
      return [
        ('version',   int  , 0),
        ('user_data', dict, {}),
      ]

class BaseTransformer(object):
  def __init__(self, _m):
    self._m = _m
    self._cfg = json.loads(_m.system.config)

  def transform(self, service):
    """
    Transforms the model into the specified service.
    """
    # This is a fallback implementation.
    # Subclasses implement actual transformation rules.
    raise UnsupportedTransformationError(service)

  def _get_converted_model(self, service, user_version, user_data, config):
    user_raw = BytesIO()

    # Write user container header to user_raw.
    pk = msgpack.Packer()
    user_raw.write(pk.pack_array_header(2))
    user_raw.write(pk.pack(user_version))
    user_raw.write(pk.pack_array_header(len(user_data)))

    # Write user_data to user_raw.
    for d in user_data:
      user_raw.write(d.getvalue())

    # Create transformed model.
    m1 = self._m
    m2 = JubaModel()
    m2.header = copy.deepcopy(m1.header)
    m2.system = copy.deepcopy(m1.system)
    m2.system.type = service
    m2.system.config = json.dumps(config)
    m2._user_raw = user_raw.getvalue()
    m2.user = JubaModel.UserContainer.loads(m2._user_raw)

    # Recompute CRC32 checksum and field lengths.
    m2.fix_header()

    return m2

class GenericTransformer(BaseTransformer):
  """
  Transformation for services having generic 2-element model data
  structure (service model and weight manager model).
  It can be converted to Weight model.
  """

  def transform(self, service):
    if service == 'weight':
      (rm, wm) = self._unpack_generic()
      return self._get_converted_model(service, 1, [wm], self._get_weight_config())
    return super(GenericTransformer, self).transform(service)

  def _unpack_generic(self, expected_version=1):
    """
    Unpacks the 2-element model data structure and returns file-like objects
    of raw service model and weight manager model.
    """
    (rm, wm) = (BytesIO(), BytesIO())
    unp = msgpack.Unpacker(BytesIO(self._m._user_raw))
    assert unp.read_array_header() == 2     # <user_container>
    assert unp.unpack() == expected_version #  +- <version>
    assert unp.read_array_header() == 2     #  +- <user_data>
    unp.unpack(rm.write)                    #      +- (service model)
    unp.unpack(wm.write)                    #      +- wm_.get_model()->pack(pk)
    rm.seek(0)
    wm.seek(0)
    return rm, wm

  def _is_method(self, *methods):
    """
    Returns True if the method used in the model is any of the specified methods.
    """
    return self._cfg['method'] in methods

  def _get_weight_config(self):
    """
    Extracts and returns the weight configuration data.
    """
    cfg = self._cfg
    return {
      'converter': cfg['converter'],
    }

  def _get_backend_config(self):
    """
    Extracts and returns the backend configuration data.
    """
    cfg = self._cfg
    return {
      'method': cfg['parameter']['method'],
      'parameter': cfg['parameter']['parameter'],
      'converter': cfg['converter'],
    }

class ClassifierTransformer(GenericTransformer):
  def transform(self, service):
    if service == 'nearest_neighbor' and self._is_method('nearest_neighbor', 'NN'):
      (rm, wm) = self._unpack_generic()
      return self._get_converted_model(service, 1, [self._extract_nn(rm), wm], self._get_backend_config())
    return super(ClassifierTransformer, self).transform(service)

  def _extract_nn(self, rm):
    nn = BytesIO()
    unp = msgpack.Unpacker(rm)
    assert unp.read_array_header() == 2   # classifier_->pack(pk)
    unp.unpack(nn.write)                  #  +- nearest_neighbor_engine_->pack(pk)
    unp.skip()                            #  +- labels_.pack(pk)
    return nn

class RegressionTransformer(ClassifierTransformer):
  # The same transformation code as Classifier can be used for Regression models.
  pass

class RecommenderTransformer(GenericTransformer):
  def transform(self, service):
    if service == 'nearest_neighbor' and self._is_method('nearest_neighbor_recommender'):
      (rm, wm) = self._unpack_generic()
      return self._get_converted_model(service, 1, [self._extract_nn(rm), wm], self._get_backend_config())
    return super(RecommenderTransformer, self).transform(service)

  def _extract_nn(self, rm):
    nn = BytesIO()
    unp = msgpack.Unpacker(rm)
    assert unp.read_array_header() == 2   # recommender_->pack(pk)
    unp.skip()                            #  +- orig_.pack(packer)
    unp.unpack(nn.write)                  #  +- nearest_neighbor_engine_->pack(pk)
    return nn

class AnomalyTransformer(GenericTransformer):
  def transform(self, service):
    if service == 'nearest_neighbor' and self._is_method('light_lof'):
      (rm, wm) = self._unpack_generic()
      return self._get_converted_model(service, 1, [self._extract_nn(rm), wm], self._get_backend_config())
    elif service == 'recommender' and self._is_method('lof'):
      (rm, wm) = self._unpack_generic()
      return self._get_converted_model(service, 1, [self._extract_recommender(rm), wm], self._get_backend_config())
    return super(AnomalyTransformer, self).transform(service)

  def _extract_nn(self, rm):
    nn = BytesIO()
    unp = msgpack.Unpacker(rm)
    assert unp.read_array_header() == 2   # anomaly_->pack(pk)
    unp.unpack(nn.write)                  #  +- nearest_neighbor_engine_->pack(pk)
    unp.skip()                            #  +- mixable_scores_->get_model()->pack(packer)
    return nn

  def _extract_recommender(self, rm):
    nn = BytesIO()
    unp = msgpack.Unpacker(rm)
    assert unp.read_array_header() == 2   # anomaly_->pack(pk)
    unp.skip()                            #  +- mixable_storage_->get_model()->pack(packer)
    unp.unpack(nn.write)                  #  +- nn_engine_->pack(packer)
    return nn

class ClusteringTransformer(GenericTransformer):
  # Only supports conversion to weight service.
  pass

class UnsupportedTransformationError(Exception):
  def __init__(self, service):
    msg = 'Error: this model cannot be transformed as {0}'.format(service)
    super(UnsupportedTransformationError, self).__init__(msg)

class InvalidModelFormatError(Exception):
  pass

class JubaModelError(Exception):
  def __init__(self, msg, e=None):
    if e:
      msg2 = 'Error: {0} ({1}): {2}'.format(msg, type(e).__name__, str(e))
    else:
      msg2 = 'Error: {0}'.format(msg)
    super(JubaModelError, self).__init__(msg2)

class _JubaModelOptionParser(optparse.OptionParser, object):
  def __init__(self, *args, **kwargs):
    self._error = False
    super(_JubaModelOptionParser, self).__init__(*args, **kwargs)

  def error(self, msg):
    print('Error: {0}'.format(msg))
    self._error = True

class _JubaModelCommand(object):
  """
  Provides command line interface for ``jubamodel`` command.
  """

  @classmethod
  def run(cls, target, in_fmt, out_fmt, output=None,
          fix_header=False, output_config=None, transform=None,
          replace_config=None, replace_version=None,
          no_validate=False):
    # Predict model file format
    if in_fmt == 'auto':
      try:
        in_fmt = JubaModel.predict_format(target)
      except InvalidModelFormatError as e:
        raise JubaModelError('{0}: invalid model file format'.format(target), e)
      except Exception as e:
        raise JubaModelError('{0}: failed to predict model format'.format(target), e)

    # Load model file
    try:
      if in_fmt == 'binary':
        with open(target, 'rb') as f:
          m = JubaModel.load_binary(f, not no_validate)
      elif in_fmt == 'json':
        with open(target, 'r') as f:
          m = JubaModel.load_json(f)
      else:
        raise ValueError(in_fmt)
    except InvalidModelFormatError as e:
      raise JubaModelError('{0}: failed to parse model as {1}'.format(target, in_fmt), e)
    except Exception as e:
      raise JubaModelError('{0}: failed to load from model'.format(target), e)

    # Transform model
    if transform:
      m = m.transform(transform)

    # Replace config file
    if replace_config is not None:
      with open(replace_config) as f:
        m.system.config = f.read()
      if not fix_header:
        printe('Warning: replacing config without fixing header; may generate corrupt model')

    # Replace version
    if replace_version is not None:
      (major, minor, maint) = map(int, replace_version.split('.'))
      m.header.jubatus_version_major = major
      m.header.jubatus_version_minor = minor
      m.header.jubatus_version_maint = maint
      if not fix_header:
        printe('Warning: replacing version without fixing header; may generate corrupt model')

    # Repair header
    if fix_header:
      try:
        m.fix_header()
      except Exception as e:
        raise JubaModelError('{0}: failed to fix header'.format(target), e)

    # Output model contents
    try:
      if out_fmt == 'binary':
        if not output:
          raise JubaModelError('output file must be specified for binary output')
        with open(output, 'wb') as f:
          m.dump_binary(f)
      elif out_fmt == 'json':
        if not output:
          m.dump_json(get_stdio()[1])  # stdout
        else:
          with open(output, 'w') as f:
            m.dump_json(f)
      elif out_fmt == 'text':
        if not output:
          m.dump_text(get_stdio()[1])  # stdout
        else:
          with open(output, 'w') as f:
            m.dump_text(f)
    except Exception as e:
      raise JubaModelError('{0}: failed to write model'.format(output), e)

    # Output config
    if output_config:
      try:
        with open(output_config, 'w') as f:
          f.write(m.system.config)
      except Exception as e:
        raise JubaModelError('{0}: failed to write config'.format(output_config), e)

  @classmethod
  def start(cls, args):
    USAGE = '''
    jubamodel [--in-format IN_FORMAT] [--out-format OUT_FORMAT]
              [--output OUTPUT] [--output-config OUTPUT_CONFIG]
              [--transform TRANSFORM]
              [--no-validate] [--fix-header]  model_file
    jubamodel --help'''

    EPILOG = '  model_file            input model file in format specified by --in-format'

    parser = _JubaModelOptionParser(add_help_option=False, usage=USAGE, epilog=EPILOG)

    # arguments
    parser.add_option('-i', '--in-format',       choices=('auto','binary','json'), default='auto',
                      help='model input format (default: %default)')
    parser.add_option('-o', '--out-format',      choices=('text','binary','json'), default='text',
                      help='model output format (default: %default)')
    parser.add_option('-O', '--output',          type='str',                       default=None,
                      help='specify output file instead of stdout')
    parser.add_option('-C', '--output-config',   type='str',                       default=None,
                      help='specify output file of config extracted from model')
    parser.add_option('-T', '--transform',       type='str',                       default=None,
                      help='transform model into another service')
    parser.add_option('-R', '--replace-config',  type='str',                       default=None,
                      help='replace configuration in model with specified file')
    parser.add_option('-Z', '--replace-version', type='str',                       default=None,
                      help='replace Jubatus version in model file')
    parser.add_option('-f', '--no-validate',     action='store_true',              default=False,
                      help='disable validation of binary model files')
    parser.add_option('-F', '--fix-header',      action='store_true',              default=False,
                      help='recompute CRC32 checksum and fix corrupt header if possible')
    parser.add_option('-h', '--help',            action='store_true',              default=False,
                      help='show usage')

    def print_usage():
      print('JubaModel - Jubatus Low-Level Model Manipulation Tool')
      print()
      parser.print_help(get_stdio()[1])  # stdout
      print()
      print('Supported Formats:')
      print('  IN_FORMAT:  auto | binary | json')
      print('  OUT_FORMAT: text | binary | json')

    (args, files) = parser.parse_args(args)

    # Failed to parse options.
    if parser._error:
      print_usage()
      return 2

    # Help option is specified.
    if args.help:
      print_usage()
      return 0

    # Validate parameters.
    if len(files) == 0:
      print('Error: no model file specified')
      print_usage()
      return 1
    if len(files) != 1:
      print('Error: cannot specify multiple model files at once')
      print_usage()
      return 1
    if args.out_format == 'binary' and args.output is None:
      print('Error: --output must be specified to output in binary format')
      print_usage()
      return 1

    success = False
    try:
      cls.run(
        target=files[0],
        in_fmt=args.in_format,
        out_fmt=args.out_format,
        output=args.output,
        output_config=args.output_config,
        transform=args.transform,
        replace_config=args.replace_config,
        replace_version=args.replace_version,
        no_validate=args.no_validate,
        fix_header=args.fix_header,
      )
      success = True
    except JubaModelError as e:
      print(e)

    return 0 if success else 3

def _main():
  """
  Entry point for ``jubamodel`` command.
  """
  sys.exit(_JubaModelCommand.start(sys.argv[1:]))
