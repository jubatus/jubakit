# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
from sklearn.base import BaseEstimator, ClusterMixin, TransformerMixin
from ..clustering import Clustering, Config, Dataset


class BaseJubatusClustering(BaseEstimator, ClusterMixin):
  """
  scikit-learn Wrapper for Jubatus Clustering.
  """

  def __init__(self, compressor_method='simple',
               bucket_size=100, compressed_bucket_size=100,
               bicriteria_base_size=10, bucket_length=2,
               forgetting_factor=0.0, forgetting_threshold=0.5,
               seed=0, embedded=True):
    """
    Creates a base class for Jubatus Clustering
    """
    self.compressor_method = compressor_method
    self.bucket_size = bucket_size
    self.compressed_bucket_size = compressed_bucket_size
    self.bicriteria_base_size = bicriteria_base_size
    self.bucket_length = bucket_length
    self.forgetting_factor = forgetting_factor
    self.forgetting_threshold = forgetting_threshold
    self.seed = seed
    self.embedded = embedded
    self.compressor_parameter = \
            self._make_compressor_parameter(self.compressor_method)
    self.fitted = False

  def _launch_clustering(self):
    """
    Launch Jubatus Clustering
    """
    raise NotImplementedError()

  def _make_compressor_parameter(self, compressor_method):
    if compressor_method == 'simple':
      return {
        'bucket_size': self.bucket_size,
      }
    elif compressor_method == 'compressive':
      return {
        'bucket_size': self.bucket_size,
        'compressed_bucket_size': self.compressed_bucket_size,
        'bicriteria_base_size': self.bicriteria_base_size,
        'bucket_length': self.bucket_length,
        'forgetting_factor': self.forgetting_factor,
        'forgetting_threshold': self.forgetting_threshold,
        'seed': self.seed
      }
    else:
      raise NotImplementedError()

  def fit_predict(self, X, y=None):
    """
    Construct clustering model and
    Predict the closest cluster each sample in X belongs to.
    """
    ids = list(range(len(X)))
    dataset = Dataset.from_data(X, ids=ids)
    self._launch_clustering()
    self.clustering_.clear()
    for _ in self.clustering_.push(dataset):
      pass
    self.fitted = True
    clusters = self.clustering_.get_core_members(light=True)
    labels = ['None'] * len(ids)
    for cluster_id, cluster in enumerate(clusters):
      for point in cluster:
        labels[int(point.id)] = cluster_id
    return labels

  def stop(self):
    self.clustering_.stop()

  def clear(self):
    self.clustering_.clear()


class BaseKFixedClustering(BaseJubatusClustering):

  def __init__(self, k=2, compressor_method='simple',
               bucket_size=100, compressed_bucket_size=100,
               bicriteria_base_size=10, bucket_length=2,
               forgetting_factor=0.0, forgetting_threshold=0.5,
               seed=0, embedded=True):
    super(BaseKFixedClustering, self).__init__(
      compressor_method, bucket_size, compressed_bucket_size, bicriteria_base_size,
      bucket_length, forgetting_factor, forgetting_threshold, seed, embedded)
    self.k = k

  def _method(self):
    raise NotImplementedError()

  def _launch_clustering(self):
    self.method = self._method()
    self.parameter = {
      'k': self.k,
      'seed': self.seed
    }
    self.config_ = Config(method=self.method, parameter=self.parameter,
                          compressor_method=self.compressor_method,
                          compressor_parameter=self.compressor_parameter)
    self.clustering_ = Clustering.run(config=self.config_,
                                      embedded=self.embedded)

  def fit(self, X, y=None):
    """
    Construct clustering model.
    """
    if len(X) < self.k:
      raise RuntimeWarning("At least k={0} points are needed \
                            but {1} points given".format(self.k, len(X)))
    dataset = Dataset.from_data(X)
    self._launch_clustering()
    self.clustering_.clear()
    for _ in self.clustering_.push(dataset): pass
    self.fitted = True
    return self

  def predict(self, X):
    """
    Predict the closest cluster each sample in X belongs to.
    """
    if not self.fitted:
      raise RuntimeError("clustering model not fitted yet.")
    dataset = Dataset.from_data(X)
    y_pred = []
    mappings = {}
    count = 0
    for idx, row_id, result in self.clustering_.get_nearest_center(dataset):
      if result not in mappings:
        mappings[result] = count
        y_pred.append(count)
        count += 1
      else:
        y_pred.append(mappings[result])
    return y_pred


class KMeans(BaseKFixedClustering):

  def _method(self):
    return 'kmeans'


class GMM(BaseKFixedClustering):

  def _method(self):
    return 'gmm'


class DBSCAN(BaseJubatusClustering):

  def __init__(self, eps=0.2, min_core_point=3,
               bucket_size=100, compressed_bucket_size=100,
               bicriteria_base_size=10, bucket_length=2,
               forgetting_factor=0.0, forgetting_threshold=0.5,
               seed=0, embedded=True):
    super(DBSCAN, self).__init__('simple', bucket_size,
                                 compressed_bucket_size, bicriteria_base_size,
                                 bucket_length, forgetting_factor,
                                 forgetting_threshold, seed, embedded)
    self.eps = eps
    self.min_core_point = min_core_point

  def _launch_clustering(self):
    self.method = 'dbscan'
    self.parameter = {
      'eps': self.eps,
      'min_core_point': self.min_core_point
    }
    self.config_ = Config(method=self.method, parameter=self.parameter,
                          compressor_method=self.compressor_method,
                          compressor_parameter=self.compressor_parameter)
    self.clustering_ = Clustering.run(config=self.config_,
                                      embedded=self.embedded)

