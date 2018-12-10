# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import copy
import random
import math

import jubatus

from .shell import JubaShell
from .compat import *
from .logger import get_logger
from ._process import _ServiceBackend

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
    self._key2type, self._key2name = BaseSchema._normalize_mapping(mapping)

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

  @staticmethod
  def _normalize_mapping(mapping):
    """
    Normalizes the schema mapping.
    """
    key2type = {}
    key2name = {}

    for (key, ent) in mapping.items():
      if isinstance(ent, (tuple, list, )):
        (key_type, key_name) = ent
      else:
        (key_type, key_name) = (ent, key)

      key2type[key] = key_type
      key2name[key] = key_name

    return key2type, key2name

  @staticmethod
  def _get_unique_mapping(mapping, fallback, key_type, name, optional=False):
    """
    Validates the schema key uniqueness.
    This is an utility method for subclasses.
    """
    if fallback == key_type:
      raise RuntimeError('{0} key cannot be specified as fallback in schema'.format(name))

    key2type, _ = BaseSchema._normalize_mapping(mapping)
    keys = [k for k in key2type.keys() if key2type[k] == key_type]
    if len(keys) == 0:
      if optional: return None
      raise RuntimeError('{0} key must be specified in schema'.format(name))
    elif 1 < len(keys):
      raise RuntimeError('{0} key must be an unique key in schema'.format(name))
    return keys[0]

  def __repr__(self):
    return '<jubakit: Schema {0}>'.format(str({'keys': self._key2name, 'types': self._key2type, 'fallback_type': self._fallback}))

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
    if v is None:
      return
    if t == self.STRING:
      if isinstance(v, bytes):
        v = v.decode()
      if isinstance(v, bool):
        """
        We avoid unicode_t(v), which results in string constant "True" / "False",
        as the default configuration of STRING features is set to unigram.
        """
        v = '1' if v else '0'
      d.add_string(k, unicode_t(v))
    elif t == self.NUMBER:
      # Empty unicode/bytes values cannot be cast to float; treat them as NA.
      if isinstance(v, (unicode_t, bytes)) and len(v) == 0:
        return
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
    if isinstance(v, bool):
      # isintance(True, int) returns True; so it should be checked first.
      return (cls.STRING, '1' if v else '0')
    elif isinstance(v, (int, long_t, float)):
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
    raise ValueError('cannot detect data type of {0}: {1}'.format(type(v), v))

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

    # ``_index`` and ``_buffer` hold the current cursor position and the
    # current "raw" (i.e. value loaded from Loader) row content currently
    # being iterated.
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

  def __repr__(self):
    if self._static:
      return '<jubakit: Static Dataset {0} records>'.format(len(self._data))
    return '<jubakit: Non-static Dataset>'

  def __iter__(self):
    """
    Iteratively access each transformed rows.
    """
    try:
      source = self._data if self._static else self._loader
      self._index = 0
      for row in source:
        if row is None:
          # May contain None in self._data if Dataset.convert is used.
          continue
        # Predict schema (for non-static Datasets)
        if self._schema is None:
          self._schema = self._predict(row)
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
    self._embedded = False
    self._backend = None

  def __del__(self):
    # Invoke the backend destructor as fast as possible.
    self._backend = None

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
  def _embedded_class(cls):
    """
    Subclasses must override this method and return the embedded class.
    """
    #return jubatus.embedded.Classifier
    raise NotImplementedError()

  @classmethod
  def run(cls, config, port=None, embedded=False):
    """
    Runs a new standalone server or embedded instance and returns the
    service instance.
    """
    if embedded:
      backend = _ServiceBackendEmbedded(cls._embedded_class(), config)
      service = cls()
      service._backend = backend
      service._embedded = True
    else:
      backend = _ServiceBackend(cls.name(), config, port)
      _logger.info('service %s started on port %d', cls.name(), backend.port)
      service = cls('127.0.0.1', backend.port)
      service._backend = backend
    return service

  def _client(self):
    if self._embedded:
      return self._backend.model
    return self._client_class()(self._host, self._port, self._cluster, self._timeout)

  def _shell(self, **kwargs):
    if self._embedded:
      raise RuntimeError('embedded service does not support shell')

    return JubaShell(
      host=self._host,
      port=self._port,
      cluster=self._cluster,
      service=self.name(),
      timeout=self._timeout,
      keepalive=True,
      **kwargs
    )

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
    if self._embedded:
      return {'127.0.0.1_0': self._backend.get_status()}
    return self._client().get_status()

  def shell(self, **kwargs):
    """
    Starts an interactive shell session for this service.
    """
    self._shell(**kwargs).interact()

  def __repr__(self):
    if self._embedded:
      return '<jubakit: Embedded Service ({0})>'.format(self.name())
    return '<jubakit: RPC Service ({0}) [{1}@{2}:{3}]{4}>'.format(
           self.name(), self._cluster, self._host, self._port,
           ', started by jubakit' if self._backend else '')

class _ServiceBackendEmbedded(object):
  def __init__(self, clazz, config):
    self.model = clazz(config)

  def stop(self):
    pass

  def get_status(self):
    """
    get_status API is not supported in embedded service.
    """
    return {}

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
      else:
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

class Utils(object):
  @staticmethod
  def softmax(x):
    max_x = max(x)
    e_x = [math.exp(x_i - max_x) for x_i in x]
    sum_e_x = sum(e_x)
    return [e_x_i / sum_e_x for e_x_i in e_x]
