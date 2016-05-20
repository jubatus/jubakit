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
from .logger import get_logger

_logger = get_logger()

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
    this method to perform custom process.  You can yield None to skip the
    record.
    """
    return ent

  def __iter__(self):
    """
    Loads each row from the data source.
    """
    for ent in self.rows():
      processed = self.preprocess(ent)
      if processed is not None:
        yield processed

  def rows(self):
    """
    Subclasses must override this method and yield each row of data source
    in flat dict-like object.  You can yield None to skip the record.
    """
    raise NotImplementedError()

class BaseSchema(object):
  """
  Schema defines data types for each key of the data.

  BaseSchema defines the fundamental 3 data types.

  - IGNORE: ignores the key (mainly intended for fallback)
  - AUTO: use the type of the key as its data type
  - INFER: guess the type of the key from its value; note that this is
           discouraged as it may result in unstable result.
  """

  # Data Types: single-character type names are reserved by jubakit.
  # External subclasses must use 2+ characters for type names.
  IGNORE = '_'
  AUTO = '.'
  INFER = '?'

  def __init__(self, mapping, fallback=None):
    """
    Defines a Schema.  Schema is an immutable object and cannot be modified.
    `mapping` is a dict-like object that maps row keys to the data type.
    Optionally you can assign an alias name for the key to handle different
    loaders with the same configuration.
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
    Transform the row (dict-like) into data structures required by the
    corresponding Service.
    """
    raise NotImplementedError()

  @classmethod
  def predict(cls, row, typed):
    """
    Predicts a Schema from dict-like row object.
    """
    raise NotImplementedError()

  def __str__(self):
    return str({'keys': self._key2name, 'types': self._key2type, 'fallback_type': self._fallback})

class GenericSchema(BaseSchema):
  """
  GenericSchema is a base Schema class for all engines using Datum.

  GenericSchema defines 3 data types:

  - STRING: string features (string_values)
  - NUMBER: numeric features (num_values)
  - BINARY: binary features (binary_values)
  """

  STRING = 's'
  NUMBER = 'n'
  BINARY = 'b'

  def transform(self, row):
    """
    Transforms the row (represented in dict-like object) as Datum.
    Subclasses that define their own data types should override this method
    and handle them.
    """
    return self._transform_as_datum(row)

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
    elif t == self.AUTO or t == self.INFER:
      (pred_type, pred_v) = self._predict_type(v, (t == self.AUTO))
      _logger.debug('key %s predicted as type %s', k, pred_type)
      self._add_to_datum(d, pred_type, k, pred_v)
    elif t == self.IGNORE:
      pass
    else:
      raise RuntimeError('invalid type {0} for key {1}'.format(t, k))

  def _transform_as_datum(self, row, d=None, skip_keys=[]):
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
  def predict(cls, row, typed):
    """
    Predicts a schema from dict-like row object.
    """
    mapping = {}
    for (k, v) in row.items():
      (mapping[k], _) = cls._predict_type(v, typed)
      _logger.info('key %s predicted as type %s', k, mapping[k])
    return cls(mapping)

  @classmethod
  def _predict_type(cls, v, typed):
    """
    Predicts a data type for the given data.
    if `typed` is True, no type conversion will be tried against `v`.
    """
    if isinstance(v, (int, long_t, float)):
      return (cls.NUMBER, v)
    elif isinstance(v, unicode_t):
      if not typed:
        try: return (cls.NUMBER, float(v))
        except ValueError: pass
      return (cls.STRING, v)
    elif isinstance(v, bytes):
      if not typed:
        try: return (cls.NUMBER, float(v))
        except ValueError: pass
        try: return (cls.STRING, v.decode())
        except UnicodeDecodeError: pass
      return (cls.BINARY, v)
    else:
      raise ValueError('cannot detect data type of {0}'.format(v.__class__))

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
    self._index = -1
    self._buffer = None

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
      _logger.info('loading all records from loader %s', loader)
      for row in loader:
        if row is None:
          continue
        # Predict schema.
        if self._schema is None:
          self._schema = self._predict(row)
        self._data.append(row)
      _logger.info('records loaded (%d entries)', len(self._data))

      # Don't hold a ref to the loader for static datasets.
      self._loader = None

  @classmethod
  def _predict(cls, row):
    """
    Predict the Schema for the given row using the corresponding Schema class.
    """
    # return GenericSchema.predict(row, False)
    raise NotImplementedError()

  def is_static(self):
    """
    Returns True for static datasets.
    """
    return self._static

  def get_schema(self):
    """
    Returns the Schema for this dataset.
    """
    return self._schema

  def shuffle(self, seed=None):
    """
    Returns a new immutable Dataset whose records are shuffled.
    """
    if not self._static:
      raise RuntimeError('non-static datasets cannot be shuffled')

    def _shuffle(data):
      return random.Random(seed).sample(data, len(data))
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

  def get(self, idx):
    """
    Returns the raw entry loaded by Loader.
    """
    if idx == self._index:
      # For convenience, even non-static datasets can access the raw record for
      # the index that is currently being iterated.
      return self._buffer

    if not self._static:
      raise RuntimeError('non-static datasets cannot be random accessed by index')
    return self._data[idx]

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
    if isinstance(index, int) and index == self._index:
      # For convenience, even non-static datasets can access the record for the
      # index that is currently being iterated.
      return self._schema.transform(self._buffer)

    if not self._static:
      raise RuntimeError('non-static datasets cannot be random accessed by index')

    if isinstance(index, slice):
      return self.__class__(self._loader, self._schema, True, self._data[index])
    elif isinstance(index, collections.Iterable):
      subdata = []
      for i in index:
        subdata.append(self._data[i])
      return self.__class__(self._loader, self._schema, True, subdata)
    else:
      return self._schema.transform(self._data[index])

  def __str__(self):
    return str(self._data)

  def __repr__(self):
    return repr(self._data)

  def __iter__(self):
    """
    Iteratively access each transformed rows.
    """
    try:
      source = self._data if self._static else self._loader
      self._index = 0
      for row in source:
        if row is None:
          continue
        self._buffer = row
        yield (self._index, self._schema.transform(row))
        self._index += 1
    finally:
      self._index = -1
      self._buffer = None
      self._loader = None

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
    _logger.info('service %s started on port %d', cls.name(), backend.port)

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
    if not self._client().clear():
      raise RuntimeError('failed to clear model')
    _logger.info('model cleared')

  def save(self, name, path=None):
    """
    Saves the model using `name`.  If `path` is specified, copy the saved
    model file to local `path`.
    """
    self._client().save(name)
    _logger.info('model saved: %s', name)
    # TODO copy source from `jubafetch` and make path option work.

  def load(self, name, path=None):
    """
    Loads the model using `name`.  If `path` is specified, copy the model
    file from local `path` to remote location.
    """
    if not self._client().load(name):
      raise RuntimeError('failed to load model: {0}'.format(name))
    _logger.info('model loaded: %s', name)
    # TODO copy source from `jubafetch` and make path option work.

  def get_status(self):
    """
    Returns the status of this server.  In distributed mode, returns statuses
    of all members.
    """
    return self._client().get_status()

class _ServiceBackend(object):
  """
  Service backend handles messy process-related things.
  """

  # Disable verbose tornado WARN logs on connect failure.
  logging.getLogger('tornado').setLevel(logging.ERROR)

  # Global Port-to-PID mapping.
  port2pid = {}

  def __init__(self, name, config, port=None):
    self.name = name
    self.config = config
    self.port = port
    self.log = None
    self._proc = None

    self._check_installed(name)

    if port is None:
      self.port = self._get_free_port()

    if port in self.port2pid:
      raise RuntimeError('port {0} currently in use by another service (PID {1})'.format(port, self.port2pid[port]))

    with tempfile.NamedTemporaryFile() as config_file:
      config_file.write(json.dumps(config).encode('utf-8'))
      config_file.flush()

      args = [
        'juba{0}'.format(name),
        '--listen_addr', '127.0.0.1',
        '--rpc-port', str(self.port),
        '--timeout', '0',
        '--configpath', config_file.name
      ]
      _logger.info('starting service: %s', args)
      self._proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      self._assign_port(self.port, self._proc.pid)

      # Wait until the RPC server start.
      started = self._wait_until_rpc_ready(self.port)
      if started:
        status = self.get_status()
        pid = int(status['pid'])
        if pid != self._proc.pid:
          self._proc.kill()
          raise RuntimeError('server cannot be started as port {0} conflicts with external Jubatus process (PID: {1})'.format(self.port, pid))

    if not started:
      _logger.error('failed to start service')
      log = self.stop()

  def __del__(self):
    proc = self._proc
    if proc is not None and proc.poll() is None:  # still running
      proc.kill()
      self._unassign_port(self.port, proc.pid)

  def stop(self):
    """
    Stops the server instance and return the server log.
    """
    proc = self._proc
    self._proc = None
    if proc is not None:
      if proc.poll() is None:  # still running
        _logger.debug('process is still running; will be terminated')
        proc.terminate()
      else:
        _logger.debug('process already terminated')

      _logger.debug('waiting for process to exit')
      (stdout, _) = proc.communicate()
      retval = proc.returncode
      _logger.debug('process exit with status %d', retval)
      self._unassign_port(self.port, proc.pid)
      if retval != 0:
        raise RuntimeError('server exit with status {0}; confirm that the config is valid: {1}'.format(retval, stdout))
      return stdout

  def get_status(self):
    cli = msgpackrpc.Client(msgpackrpc.Address('127.0.0.1', self.port), unpack_encoding='utf-8')
    try:
      return cli.call('get_status', '')['127.0.0.1_{0}'.format(self.port)]
    finally:
      cli.close()

  @classmethod
  def _get_free_port(cls, start=10000, end=30000):
    """
    Finds the free port available to listen.

    The default range of [10000,30000] is chosen to avoid the default
    ephemeral port range on most platforms.
    """
    used_ports = cls._get_ports_in_use()
    port = start
    while True:
      if port not in used_ports: return port
      port += 1
      if end < port:
        raise RuntimeError('no free port available in range [{0},{1}]'.format(start, end))

  @classmethod
  def _get_ports_in_use(cls):
    """
    Returns sorted list of ports currently used on localhost.
    """
    try:
      return sorted(set([x.laddr[1] for x in psutil.net_connections(kind='inet4')]))
    except psutil.AccessDenied:
      # On some platforms (such as OS X), root privilege is required to get used ports.
      # In that case we avoid port confliction to the best of our knowledge.
      _logger.info('ports in use cannot be obtained on this platform; ports will be assigned sequentially')
      return sorted(cls.port2pid.keys())

  @classmethod
  def _assign_port(cls, port, pid):
    m = cls.port2pid
    if port in m:
      raise RuntimeError('port {0} currently in use by PID {1}'.format(port, m[port]))
    m[port] = pid

  @classmethod
  def _unassign_port(cls, port, pid):
    m = cls.port2pid
    if m is None:
      pass   # maybe destruction is running.
    if port not in m:
      raise RuntimeError('port {0} is not in use'.format(port))
    if m[port] != pid:
      raise RuntimeError('port {0} is used by PID {1}, not PID {2}'.format(port, m[port], pcid))
    del m[port]

  @classmethod
  def _wait_until_rpc_ready(cls, port):
    sleep_time = 1000
    for i in range(10):
      time.sleep(sleep_time/1000000.0) # from usec to sec
      if cls._ping_rpc(port):
        return True
      sleep_time *= 2
    _logger.debug('service RPC ready in %d tries', i)
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
  def _check_installed(cls, name):
    procname = 'juba{0}'.format(name)

    _logger.debug('checking if service process %s is available', procname)
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

    if method is not None:
      self['method'] = method
      default_parameter = self._default_parameter(method)
      if default_parameter is None:
        if 'parameter' in self: del self['parameter']
      elif default_parameter is not None:
        self['parameter'] = default_parameter

    if parameter is not None:
      if 'parameter' in self:
        self['parameter'].update(parameter)
      else:
        self['parameter'] = parameter

    if converter is not None:
      if 'converter' in self:
        self['converter'].update(converter)
      else:
        self['converter'] = converter

  @classmethod
  def _default(cls, cfg):
    cfg.clear()

    method = cls._default_method()
    parameter = cls._default_parameter(method)
    converter = cls._default_converter()

    if method    is not None: cfg['method'] = method
    if parameter is not None: cfg['parameter'] = parameter
    if converter is not None: cfg['converter'] = converter

  @classmethod
  def _default_method(cls):
    """
    Subclasses must override this method and return the preferred default
    method.
    """
    #return 'AROW'
    raise NotImplementedError()

  @classmethod
  def _default_parameter(cls, method):
    """
    Subclasses must override this method and return the preferred default
    parameter set for the specified method.  Return `None` if  the method
    does not require `parameter` block.
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

  @classmethod
  def methods(cls):
    """
    Subclasses must override this method and return methods available for
    this service.
    """
    #return ['perceptron', 'PA', 'AROW']
    raise NotImplementedError()

  def clear_converter(self):
    """
    Initialize the `converter` section of the config with an empty template.
    """
    self['converter'] = copy.deepcopy(self._CONVERTER_TEMPLATE)

  def add_mecab(self, name='mecab', arg='', ngram=1, base=False, include_features='*', exclude_features=''):
    """
    Add MeCab feature extraction to string_types.
    """
    if isinstance(include_features, list):
      include_features = '|'.join(include_features)

    if isinstance(exclude_features, list):
      exclude_features = '|'.join(exclude_features)

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
