# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import copy
import json
import random
import time
import logging
import subprocess
import tempfile

import jubatus
import msgpackrpc
import psutil

from .compat import *

class BaseLoader(object):
  """
  Loader loads rows from various data sources.
  """

  def is_infinite(self):
    """
    Returns True if the length of the data source is indeterminate (e.g., MQ.)
    """
    return False

  def preprocess(self, ent):
    """
    Preprocesses the given dict-like object into another dict-like object.
    The default implementation does not alter the object.  Users can override
    this method to perform custom process.
    """
    return ent

  def __iter__(self):
    """
    Subclasses must override this method and yield each row of data source
    in dict-like object.  You can yield None to skip the record.
    """
    raise NotImplementedError()

class BaseSchema(object):
  """
  Schema defines data types for each key of the data.
  """

  # Data Types: single-character type names are reserved by jubakit.
  # External subclasses must use 2+ characters for type names.
  STRING = 's'
  NUMBER = 'n'
  BINARY = 'b'

  def __init__(self, mapping, fallback=None):
    """
    Defines a Schema.  Schema is an immutable object and cannot be modified.
    `mapping` is a dict-like object that maps row keys to the data type.
    Optionally you can assign an alias name for the key to handle different
    oaders with the same configuration.
    """
    self._fallback = fallback
    self._key2type = {}
    self._key2name = {}

    for (key, ent) in mapping.items():
      if isinstance(ent, (tuple, list, )):
        (key_type, key_name) = ent
      else:
        (key_type, key_name) = (ent, key)

      self._key2type[key] = key_type
      self._key2name[key] = key_name

  def transform(self, row):
    """
    Transforms the row (represented in dict-like object) as Datum.
    Subclasses that define their own data types should override this method
    and handle them.
    """
    return self.transform_as_datum(row)

  def _add_to_datum(self, d, t, k, v):
    """
    Add value `v` whose type and name are `t` and `k` resp. to Datum `d`.
    """
    if t == self.STRING:
      d.add_string(k, unicode_t(v))
    elif t == self.NUMBER:
      d.add_number(k, float(v))
    elif t == self.BINARY:
      d.add_binary(k, v)
    else:
      raise RuntimeError('invalid type {0} for key {1}'.format(t, k))

  def transform_as_datum(self, row, d=None, skip_keys=[]):
    """
    Transforms the row as Datum.  If the original Datum `d` is specified,
    feature vectors will be added to it.
    """
    if d is None:
      d = jubatus.common.Datum()

    for (key, value) in row.items():
      if key in skip_keys:
        continue

      key_type = self._key2type.get(key, self._fallback)
      key_name = self._key2name.get(key, key)
      if key_type is None:
        raise RuntimeError('schema does not match: unknown key {0}'.format(key))
      self._add_to_datum(d, key_type, key_name, value)

    return d

  @classmethod
  def predict(cls, row):
    """
    Predicts a schema from dict-like row object.
    """
    mapping = {}
    for (k, v) in row.items():
      t = cls.NUMBER
      try:
        float(v)
      except:
        t = cls.STRING
      mapping[k] = t
    return cls(mapping)

class BaseDataset(object):
  """
  Dataset is an abstract representation of set of data.
  """

  def __init__(self, loader, schema=None, static=None, _data=None):
    """
    Defines a new dataset.  Datasets are immutable and cannot be modified.

    Data will be loaded from the given `loader` using `schema`.

    When `static` is set to True (which is the default for non-infinite
    loaders), data will be loaded on memory immedeately; otherwise data
    will be loaded one-by-one from `loader`, which may be better when processing
    a large dataset.  For "infinite" loaders (like MQ and Twitter stream),
    `static` cannot be set to True.  Note that some features
    (e.g., index access) are not available for non-static datasets, which
    may be needed for some features like cross-validation etc.
    """
    self._loader = loader
    self._schema = schema

    if static is None:
      # Non-infinite loaders are static by default.
      static = not loader.is_infinite()

    self._static = static

    # `_data` is internally used to create a shallow subset of the Dataset.
    if _data is None:
      self._data = []
    else:
      self._data = _data
      return  # the data is already loaded

    if static:
      if loader.is_infinite():
        # Infinite data sources (e.g., MQ) cannot be loaded statically on memory.
        raise RuntimeError('infinite loaders cannot be staticized')

      # Load all data entries.
      for row in loader:
        if row is None:
          continue
        # Predict schema.
        if self._schema is None:
          self._schema = BaseSchema.predict(row)
        self._data.append(self._schema.transform(row))

      # Don't hold a ref to the loader for static datasets.
      self._loader = None

  def is_static(self):
    """
    Returns True for static datasets.
    """
    return self._static

  def shuffle(self):
    """
    Returns a new immutable Dataset whose records are shuffled.
    """
    if not self._static:
      raise RuntimeError('non-static datasets cannot be shuffled')

    def _shuffle(data):
      return random.sample(data, len(data))
    return self.convert(_shuffle)

  def convert(self, func):
    """
    Applies the given callable (which is expected to perform batch
    pre-processing like `shuffle`) to the whole data entries and returns
    a new immutable Dataset.
    """
    if not self._static:
      raise RuntimeError('non-static datasets cannot be converted')
    new_data = func(self._data)
    if not isinstance(new_data, collections.Iterable):
      raise RuntimeError('convert function returned non-iterable: {0}'.format(new_data.__class__))

    return self.__class__(self._loader, self._schema, True, new_data)

  def __len__(self):
    """
    Returns the number of entries.
    """
    if not self._static:
      raise RuntimeError('length of non-static datasets cannot be retrieved')
    return len(self._data)

  def __getitem__(self, index):
    """
    Returns row(s) at the position `index`.
    `index` can be an iterable (like numpy array) or just an int.
    """
    if not self._static:
      raise RuntimeError('non-static datasets cannot be accessed by index')

    if isinstance(index, slice):
      return self.__class__(self._loader, self._schema, True, self._data[index])
    elif isinstance(index, collections.Iterable):
      subdata = []
      for i in index:
        subdata.append(self._data[i])
      return self.__class__(self._loader, self._schema, True, subdata)
    else:
      return self._data[index]

  def __str__(self):
    return str(self._data)

  def __repr__(self):
    return repr(self._data)

  def __iter__(self):
    """
    Iteratively access each transformed rows.
    """
    idx = 0
    if self._static:
      for row in self._data:
        yield (idx, row)
        idx += 1
    else:
      for row in self._loader:
        if row is None:
          continue
        yield (idx, self._schema.transform(row))
        idx += 1

class BaseService(object):
  """
  Service provides an interface to machine learning features.
  """

  def __init__(self, host='127.0.0.1', port=9199, cluster='', timeout=0):
    """
    Creates a new service that connects to the exsiting server.
    """
    self._host = host
    self._port = port
    self._cluster = cluster
    self._timeout = timeout
    self._backend = None

  def __del__(self):
    """
    Destroys the backend process if exists.
    """
    backend = self._backend
    if backend is not None:
      backend.stop()

  @classmethod
  def name(cls):
    """
    Subclasses (Classifier, NearestNeighbor, ... etc.) must override this
    method and return its service name (classifier, nearest_neighbor, ... etc.)
    """
    #return 'classifier'
    raise NotImplementedError()

  @classmethod
  def _client_class(cls):
    """
    Subclasses must override this method and return the client class.
    """
    #return jubatus.classifier.client.Classifier
    raise NotImplementedError()

  @classmethod
  def run(cls, config, port=None):
    """
    Runs a new standalone server and returns the serivce instance to access
    the server.
    """
    backend = _ServiceBackend(cls.name(), config, port)

    # Returns the Service instance.
    service = cls('127.0.0.1', backend.port)
    service._backend = backend
    return service

  def _client(self):
    return self._client_class()(self._host, self._port, self._cluster, self._timeout)

  def stop(self):
    """
    Stops the backend process if exists.
    """
    if self._backend is not None:
      return self._backend.stop()

  def clear(self):
    """
    Clears the model.
    """
    self._client().clear()

  def save(self, name, path=None):
    """
    Saves the model using `name`.  If `path` is specified, copy the saved
    model file to local `path`.
    """
    self._client().save(name)
    # TODO copy source from `jubafetch` and make path option work.

  def load(self, name, path=None):
    """
    Loads the model using `name`.  If `path` is specified, copy the model
    file from local `path` to remote location.
    """
    self._client().load(name)
    # TODO copy source from `jubafetch` and make path option work.

class _ServiceBackend(object):
  """
  Service backend handles messy process-related things.
  """

  # Disable verbose tornado WARN logs on connect failure.
  logging.getLogger('tornado').setLevel(logging.ERROR)

  assigned_ports = {}

  def __init__(self, name, config, port=None):
    self.name = name
    self.config = config
    self.port = port
    self.log = None
    self._proc = None

    self.check_installed(name)

    if port is None:
      self.port = self.get_next_free_port()

    with tempfile.NamedTemporaryFile() as config_file:
      json.dump(config, config_file)
      config_file.flush()

      self._proc = subprocess.Popen([
        'juba{0}'.format(name),
        '--listen_addr', '127.0.0.1',
        '--rpc-port', str(self.port),
        '--timeout', '0',
        '--configpath', config_file.name
      ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      self.lock_port(self._proc.pid, self.port)
      started = self.wait_until_rpc_ready(self.port)

    if not started:
      self.stop()

  def __del__(self):
    proc = self._proc
    if proc is not None and proc.poll() is None:  # still running
      proc.kill()
      self.unlock_port(proc.pid, self.port)

  def stop(self):
    """
    Stops the server instance and return the server log.
    """
    proc = self._proc
    self._proc = None
    if proc is not None:
      if proc.poll() is None:  # still running
        proc.terminate()

      (stdout, _) = proc.communicate()
      retval = proc.returncode
      self.unlock_port(proc.pid, self.port)
      if retval != 0:
        raise RuntimeError('server exit with status {0}; confirm that the config is valid: {1}'.format(retval, stdout))
      return stdout

  @classmethod
  def get_next_free_port(cls, start=10000, end=30000):
    try:
      used_ports = set(map(lambda x: x.laddr[1], psutil.net_connections(kind='inet4')))
    except psutil.AccessDenied:
      # On some platforms (such as OS X), root privilege is required to get used ports.
      # In that case we avoid port confliction to the best of our knowledge.
      used_ports = cls.locked_ports().values()

    port = start
    while True:
      if port not in used_ports: return port
      port += 1
      if end < port:
        raise RuntimeError('no free port available in range [{0},{1}]'.format(start, end))

  @classmethod
  def lock_port(cls, pid, port):
    cls.locked_ports()[pid] = port

  @classmethod
  def unlock_port(cls, pid, port):
    ports = cls.locked_ports()
    if pid in ports:
      del ports[pid]

  @classmethod
  def locked_ports(cls):
    ports = cls.assigned_ports
    if ports is not None:
      return ports
    return {}

  @classmethod
  def wait_until_rpc_ready(cls, port):
    sleep_time = 1000
    for i in range(10):
      time.sleep(sleep_time/1000000.0) # from usec to sec
      if cls._ping_rpc(port):
        return True
      sleep_time *= 2
    return False

  @classmethod
  def _ping_rpc(cls, port):
    cli = msgpackrpc.Client(msgpackrpc.Address("127.0.0.1", port))
    try:
      cli.call('__ping__')
      raise AssertionError('dummy RPC succeeded')
    except msgpackrpc.error.RPCError as e:
      if e.args[0] == 1:  # "no such method"
        return True
    except:
      return False
    finally:
      cli.close()

    return False

  @classmethod
  def check_installed(cls, name):
    procname = 'juba{0}'.format(name)
    try:
      proc = subprocess.Popen(
        [procname, '--version'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
      )
      (stdout, _) = proc.communicate()
      if proc.returncode == 0:
        return
      raise RuntimeError('{0} exit with status {1}; confirm that (DY)LD_LIBRARY_PATH is properly set: {2}'.format(procname, proc.returncode, stdout))
    except OSError as e:
      raise RuntimeError('{0} could not be started; confirm that PATH is properly set: {1}'.format(procname, e))

class BaseConfig(dict):
  """
  Config is a convenient class to build new config.
  """

  def __init__(self, *args, **kwargs):
    """
    Creates a new Config with default configuration.
    """
    super(BaseConfig, self).__init__(self)
    self._default(self)

  @classmethod
  def _default(cls, cfg):
    """
    Initializes the given config (dict-like) with the default configuration.
    """
    raise NotImplementedError()

  @classmethod
  def default(cls):
    """
    Returns a new default configuration.
    """
    cfg = {}
    cls._default(cfg)
    return cfg

class GenericConfig(BaseConfig):
  """
  GenericConfig is a base Config class for generic services that have
  `converter`, `method` and `parameter` in its config data.
  """

  _CONVERTER_TEMPLATE = {
    'string_filter_types' : {},
    'string_filter_rules' : [],
    'num_filter_types' : {},
    'num_filter_rules' : [],
    'string_types' : {},
    'string_rules' : [],
    'num_types': {},
    'num_rules': [],
    'binary_types': {},
    'binary_rules': [],
  }

  def __init__(self, method=None, parameter=None, converter=None):
    super(GenericConfig, self).__init__(self)
    if method    is not None: self['method'] = method
    if parameter is not None: self['parameter'] = parameter
    if converter is not None: self['converter'] = converter

  @classmethod
  def _default(cls, cfg):
    cfg.clear()

    method = cls._default_method()
    parameter = cls._default_parameter()
    converter = cls._default_converter()

    if method    is not None: cfg['method'] = method
    if parameter is not None: cfg['parameter'] = cls._default_parameter()
    if converter is not None: cfg['converter'] = cls._default_converter()

  @classmethod
  def _default_method(cls):
    """
    Subclasses must override this method and return the preferred default
    method.
    """
    #return 'AROW'
    raise NotImplementedError()

  @classmethod
  def _default_parameter(cls):
    """
    Subclasses must override this method and return the preferred default
    parameter set that match with the default method.  Return `None` if
    the method does not require `parameter` block.
    """
    #return {'regularization_weight': 0.1}
    raise NotImplementedError()

  @classmethod
  def _default_converter(cls):
    """
    Returns a default converter contents.
    """
    cfg = copy.deepcopy(cls._CONVERTER_TEMPLATE)
    cfg['string_types'] = {
      'unigram': {'method': 'ngram', 'char_num': '1'},
      'bigram':  {'method': 'ngram', 'char_num': '2'},
      'trigram': {'method': 'ngram', 'char_num': '3'},
    }
    cfg['string_rules'] = [
      {'key': '*', 'type': 'unigram', 'sample_weight': 'tf', 'global_weight': 'idf'}
    ]
    cfg['num_rules'] = [
      {'key': '*', 'type': 'num'}
    ]

    return cfg

  def clear_converter(self):
    """
    Initialize the `converter` section of the config with an empty template.
    """
    self['converter'] = copy.deepcopy(self._CONVERTER_TEMPLATE)

  def add_mecab(self, name='mecab', arg='', ngram=1, base=False, include_features='*', exclude_features=''):
    self['converter']['string_types'][name] = {
      'method': 'dynamic',
      'path': 'libmecab_splitter.so',
      'function': 'create',
      'arg': arg,
      'ngram': str(ngram),
      'base': 'true' if base else 'false',
      'include_features': include_features,
      'exclude_features': exclude_features,
    }
