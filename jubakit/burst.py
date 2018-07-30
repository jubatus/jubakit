# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import uuid

import jubatus
import jubatus.embedded

from .base import GenericSchema, BaseDataset, BaseService, GenericConfig, Utils
from .loader.array import ArrayLoader, ZipArrayLoader
from .loader.sparse import SparseMatrixLoader
from .loader.chain import ValueMapChainLoader, MergeChainLoader
from .compat import *


def _try_convert_str_to_float(value, label):
  """
  Try to convert input value to float value.
  """
  try:
    return float(value)
  except Exception:
    msg = 'Invalid parameter: {} cannot cast string to float.'.format(label)
    raise ValueError(msg)


class KeywordSchema(GenericSchema):
  """
  Keyword schema for Burst service.
  """
  KEYWORD = 'k'
  SCALING = 's'
  GAMMA = 'g'

  def __init__(self, mapping, fallback=None):
    super(KeywordSchema, self).__init__(mapping, fallback)
    self._keyword_key = self._get_unique_mapping(
      mapping, fallback, self.KEYWORD, 'KEYWORD', True)
    self._scaling_key = self._get_unique_mapping(
      mapping, fallback, self.SCALING, 'SCALING', True)
    self._gamma_key = self._get_unique_mapping(
      mapping, fallback, self.GAMMA, 'GAMMA', True)

  def transform(self, row):
    keyword = row.get(self._keyword_key, None)
    scaling = row.get(self._scaling_key, None)
    gamma = row.get(self._gamma_key, None)

    if keyword is None:
      raise RuntimeError('Row without keyword column cannot be used.')

    if scaling is not None:
      scaling = _try_convert_str_to_float(scaling, 'SCALING')
      if scaling <= 1:
        raise ValueError('Scaling parameter must be greater than 1.0.')

    if gamma is not None:
      gamma = _try_convert_str_to_float(gamma, 'GAMMA')
      if gamma <= 0:
        raise ValueError('Gamma must be greater than 1.0.')

    return (keyword, scaling, gamma)


class DocumentSchema(GenericSchema):
  """
  Document schema for Burst service.
  """
  POSITION = 'p'
  TEXT = 't'

  def __init__(self, mapping, fallback=None):
    super(DocumentSchema, self).__init__(mapping, fallback)
    self._pos_key = self._get_unique_mapping(
        mapping, fallback, self.POSITION, 'POSITION', True)
    self._text_key = self._get_unique_mapping(
        mapping, fallback, self.TEXT, 'TEXT', True)

  def transform(self, row):
    pos = row.get(self._pos_key, None)
    if pos is None:
      raise RuntimeError('Row without position column cannot be used.')
    pos = _try_convert_str_to_float(pos, 'POSITION')
    text = row.get(self._text_key, None)
    if text is None:
      text = ''
    return (pos, text)


class KeywordDataset(BaseDataset):
  """
  Keyword dataset for Burst service.
  """
  def _predict(cls, row):
    return KeywordSchema.predict(row, False)


class DocumentDataset(BaseDataset):
  """
  Document dataset for Burst service.
  """
  def _predict(cls, row):
    return DocumentSchema.predict(row, False)


class Burst(BaseService):
  """
  Burst service.
  """

  DEFAULT_SCALING = 1.1
  DEFAULT_GAMMA = 0.1

  @classmethod
  def name(cls):
    return 'burst'

  @classmethod
  def _client_class(cls):
    return jubatus.burst.client.Burst

  @classmethod
  def _embedded_class(cls):
    return jubatus.embedded.Burst

  def add_keyword(self, keyword_dataset):
    """
    Registers the keyword for burst detection.
    """
    cli = self._client()

    for idx, (keyword, scaling, gamma) in keyword_dataset:
      if scaling is None:
        scaling = Burst.DEFAULT_SCALING
      if gamma is None:
        gamma = Burst.DEFAULT_GAMMA
      result = cli.add_keyword(
          jubatus.burst.types.KeywordWithParams(keyword, scaling, gamma))
      yield (idx, result)

  def add_documents(self, document_dataset):
    """
    Register the document for burst detection.
    """
    cli = self._client()
    for (idx, (pos, text)) in document_dataset:
      if pos is None:
        raise RuntimeError('Document dataset without position ' +
                           'column cannot be used.')
      result = cli.add_documents([jubatus.burst.types.Document(pos, text)])
      yield (idx, result)

  def get_result(self, keyword):
    """
    Returns the burst detection result of the current window
    for pre-registered keyword keyword.
    """
    print('get_result')
    keyword = str(keyword)
    cli = self._client()
    return cli.get_result(keyword)

  def get_result_at(self, keyword, pos):
    """
    Returns the burst detection result at the specified
    position for pre-registered keyword.
    """
    pos = _try_convert_str_to_float(pos, 'position')
    keyword = str(keyword)
    cli = self._client()
    return cli.get_result_at(keyword, pos)

  def get_all_bursted_results(self):
    """
    Returns the burst detection result of the current window
    for all pre-registered keywords.
    """
    cli = self._client()
    return cli.get_all_bursted_results()

  def get_all_bursted_results_at(self, pos):
    """
    Returns the burst detection result at the specified
    position for all pre-registered keywords.
    """
    pos = _try_convert_str_to_float(pos, 'position')
    cli = self._client()
    return cli.get_all_bursted_results_at(float(pos))

  def get_all_keywords(self):
    """
    Returns the list of keywords registered for burst detection.
    """
    cli = self._client()
    return cli.get_all_keywords()

  def remove_keyword(self, keyword):
    """
    Removes the keyword from burst detection.
    """
    keyword = str(keyword)
    cli = self._client()
    return cli.remove_keyword(keyword)

  def remove_all_keywords(self):
    """
    Removes all the keywords from burst detection.
    """
    cli = self._client()
    return cli.remove_all_keywords()


class Config(GenericConfig):
  """
  Configurations to run Burst service.
  """

  def __init__(self, method=None, parameter=None, converter=None):
    super(Config, self).__init__(method, parameter, converter)
    if 'converter' in self:
      del self['converter']

  @classmethod
  def methods(cls):
    return ['burst']

  @classmethod
  def _default_method(cls):
    return 'burst'

  @classmethod
  def _default(cls, cfg):
    cfg.clear()

    method = cls._default_method()
    parameter = cls._default_parameter(method)

    if method    is not None: cfg['method'] = method
    if parameter is not None: cfg['parameter'] = parameter

  @classmethod
  def _default_parameter(cls, method):
    if method != 'burst':
      raise RuntimeError('unknown method: {0}'.format(method))
    return {
      "window_batch_size": 5,
      "batch_interval": 10,
      "max_reuse_batch_num": 5,
      "costcut_threshold": -1,
      "result_window_rotate_size": 5
    }
