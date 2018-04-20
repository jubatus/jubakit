# -*- coding: utf-8 -*-

"""
*Dumb* Service is a kind of temporary implementations of Services.
They are defined just for convenience.

Unlike *Real* Services (Classifier, Anomaly, ...) which are defined
in each file (classifier.py, anomaly.py, ...), Dumb Services cannot
handle Datasets and Schemas.

Each service has a field called ``CONFIG``, which provides a default
config data structure for the service.  So you can use jubakit to start
a Jubatus server processe, then directly use the raw Client class to
make RPC calls.

  >>> from jubakit.dumb import Stat
  >>> service = Stat.run(Stat.CONFIG)
  >>> client = service._client()
  >>> client.push('x', 12)
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from jubakit.base import BaseService

import jubatus
import jubatus.embedded

class Bandit(BaseService):
  CONFIG = {'method': 'ucb1', 'parameter': {'assume_unrewarded': False}}

  @classmethod
  def name(cls):           return 'bandit'
  @classmethod
  def _client_class(cls):  return jubatus.bandit.client.Bandit
  @classmethod
  def _embedded_class(cls):  return jubatus.embedded.Bandit

class Burst(BaseService):
  CONFIG = {'method': 'burst', 'parameter': {'result_window_rotate_size': 5, 'max_reuse_batch_num': 5, 'batch_interval': 10, 'window_batch_size': 5, 'costcut_threshold': -1}}

  @classmethod
  def name(cls):           return 'burst'
  @classmethod
  def _client_class(cls):  return jubatus.burst.client.Burst
  @classmethod
  def _embedded_class(cls):  return jubatus.embedded.Burst

class Clustering(BaseService):
  CONFIG = {'method': 'kmeans', 'parameter': {'k': 3, 'seed': 0}, 'compressor_method': 'simple', 'compressor_parameter': {'bucket_size': 1000}, 'distance': 'euclidean', 'converter': {'string_types': {'bigram': {'method': 'ngram', 'char_num': '2'}, 'trigram': {'method': 'ngram', 'char_num': '3'}, 'unigram': {'method': 'ngram', 'char_num': '1'}}, 'num_filter_types': {}, 'num_rules': [{'type': 'num', 'key': '*'}], 'num_filter_rules': [], 'string_filter_rules': [], 'num_types': {}, 'string_filter_types': {}, 'string_rules': [{'sample_weight': 'tf', 'global_weight': 'idf', 'type': 'bigram', 'key': '*'}]}}

  @classmethod
  def name(cls):           return 'clustering'
  @classmethod
  def _client_class(cls):  return jubatus.clustering.client.Clustering
  @classmethod
  def _embedded_class(cls):  return jubatus.embedded.Clustering

class Graph(BaseService):
  CONFIG = {'method': 'graph_wo_index', 'parameter': {'damping_factor': 0.9, 'landmark_num': 5}}

  @classmethod
  def name(cls):           return 'graph'
  @classmethod
  def _client_class(cls):  return jubatus.graph.client.Graph
  @classmethod
  def _embedded_class(cls):  return jubatus.embedded.Graph

class NearestNeighbor(BaseService):
  CONFIG = {'method': 'lsh', 'parameter': {'hash_num': 64}, 'converter': {'string_types': {'bigram': {'method': 'ngram', 'char_num': '2'}, 'trigram': {'method': 'ngram', 'char_num': '3'}, 'unigram': {'method': 'ngram', 'char_num': '1'}}, 'num_filter_types': {}, 'num_rules': [{'type': 'num', 'key': '*'}], 'num_filter_rules': [], 'string_filter_rules': [], 'num_types': {}, 'string_filter_types': {}, 'string_rules': [{'sample_weight': 'tf', 'global_weight': 'idf', 'type': 'bigram', 'key': '*'}]}}

  @classmethod
  def name(cls):           return 'nearest_neighbor'
  @classmethod
  def _client_class(cls):  return jubatus.nearest_neighbor.client.NearestNeighbor
  @classmethod
  def _embedded_class(cls):  return jubatus.embedded.NearestNeighbor

class Recommender(BaseService):
  CONFIG = {'method': 'inverted_index', 'converter': {'string_types': {'bigram': {'method': 'ngram', 'char_num': '2'}, 'trigram': {'method': 'ngram', 'char_num': '3'}, 'unigram': {'method': 'ngram', 'char_num': '1'}}, 'num_filter_types': {}, 'num_rules': [{'type': 'num', 'key': '*'}], 'num_filter_rules': [], 'string_filter_rules': [], 'num_types': {}, 'string_filter_types': {}, 'string_rules': [{'sample_weight': 'tf', 'global_weight': 'idf', 'type': 'bigram', 'key': '*'}]}}

  @classmethod
  def name(cls):           return 'recommender'
  @classmethod
  def _client_class(cls):  return jubatus.recommender.client.Recommender
  @classmethod
  def _embedded_class(cls):  return jubatus.embedded.Recommender

class Regression(BaseService):
  CONFIG = {'method': 'PA1', 'parameter': {'sensitivity': 0.1, 'regularization_weight': 3.402823e+38}, 'converter': {'string_types': {'bigram': {'method': 'ngram', 'char_num': '2'}, 'trigram': {'method': 'ngram', 'char_num': '3'}, 'unigram': {'method': 'ngram', 'char_num': '1'}}, 'num_filter_types': {}, 'num_rules': [{'type': 'num', 'key': '*'}], 'num_filter_rules': [], 'string_filter_rules': [], 'num_types': {}, 'string_filter_types': {}, 'string_rules': [{'sample_weight': 'tf', 'global_weight': 'idf', 'type': 'bigram', 'key': '*'}]}}

  @classmethod
  def name(cls):           return 'regression'
  @classmethod
  def _client_class(cls):  return jubatus.regression.client.Regression
  @classmethod
  def _embedded_class(cls):  return jubatus.embedded.Regression

class Stat(BaseService):
  CONFIG = {'window_size': 128}

  @classmethod
  def name(cls):           return 'stat'
  @classmethod
  def _client_class(cls):  return jubatus.stat.client.Stat
  @classmethod
  def _embedded_class(cls):  return jubatus.embedded.Stat
