# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from ..regression import Regression, Config, Dataset


class BaseJubatusRegression(BaseEstimator, RegressorMixin):
  """
  scikit-learn Wrapper for Jubatus Regressions.
  """

  def __init__(self, n_iter=1, shuffle=False, embedded=True, seed=None):
    """
    Creates a base class for Jubatus Regressoions.
    """
    self.n_iter = n_iter
    self.shuffle = shuffle
    self.embedded = embedded
    self.seed = seed

  @classmethod
  def _launch_regression(self):
    """
    Launch Jubatus Regression
    """
    raise NotImplementedError()

  def partial_fit(self, X, y):
    """
    Partially fit underlying model.
    If underlying model does not exist, launch a new model.
    """
    if getattr(self, 'regression_', None) is None:
      self._launch_regression()
      self.regression_.clear()
    dataset = Dataset.from_data(X, y)
    for i in range(self.n_iter):
      if self.shuffle:
        dataset = dataset.shuffle(self.seed)
      for _ in self.regression_.train(dataset): pass
    return self

  def fit(self, X, y):
    """
    Fit model.
    """
    self._launch_regression()
    self.regression_.clear()
    return self.partial_fit(X, y)

  def predict(self, X):
    """
    Predict class labels for samples in X.
    """
    if getattr(self, 'regression_', None) is None:
      raise RuntimeError('This estimator instance is not fitted yet.')
    y_pred = np.empty(X.shape[0], dtype=float)
    dataset = Dataset.from_data(X)
    for idx, _, result in self.regression_.estimate(dataset):
      y_pred[idx] = result
    return y_pred

  @classmethod
  def get_params(self, deep=True):
    """
    Return parameters.
    """
    raise NotImplementedError()

  def set_params(self, **params):
    """
    Set parameters
    """
    for param, value in params.items():
      setattr(self, param, value)
    return self

  def save(self, name):
    """
    Save the regression model using name.
    """
    if self.regression_ is not None:
      self.regression_.save(name)

  def load(self, name):
    """
    Load the regression model using name.
    """
    self._launch_regression()
    self.regression_.load(name)
    return self

  def stop(self):
    """
    Stop the backend process if exists.
    """
    if not self.embedded and self.regression_ is not None:
      self.regression_.stop()
      self.regression_ = None


class LinearRegression(BaseJubatusRegression):

  def __init__(self, method='AROW', regularization_weight=1.0, sensitivity=1.0, learning_rate=1.0,
               n_iter=1, shuffle=False, embedded=True, seed=None):
    super(LinearRegression, self).__init__(n_iter, shuffle, embedded, seed)
    self.method = method
    self.regularization_weight = regularization_weight
    self.sensitivity = sensitivity
    self.learning_rate = learning_rate

  def _launch_regression(self):
    if self.method in ('perceptron'):
      self.config_ = Config(method=self.method,
                            parameter={'learning_rate': self.learning_rate})
    if self.method in ('PA'):
      self.config_ = Config(method=self.method,
                            parameter={'sensitivity': self.sensitivity})
    elif self.method in ('PA1', 'PA2', 'CW', 'AROW', 'NHERD'):
      self.config_ = Config(method=self.method,
                            parameter={'regularization_weight': self.regularization_weight,
                                       'sensitivity': self.sensitivity})
    else:
      raise NotImplementedError('method {} is not implememented yet.'.format(self.method))
    self.regression_ = Regression.run(config=self.config_, embedded=self.embedded)

  def get_params(self, deep=True):
    return {
      'method': self.method,
      'regularization_weight': self.regularization_weight,
      'sensitivity': self.sensitivity,
      'learning_rate': self.learning_rate,
      'n_iter': self.n_iter,
      'shuffle': self.shuffle,
      'embedded': self.embedded,
      'seed': self.seed
    }


class NearestNeighborsRegression(BaseJubatusRegression):

  def __init__(self, method='euclid_lsh', nearest_neighbor_num=5,
               hash_num=128, n_iter=1, shuffle=False, embedded=True, seed=None):
    super(NearestNeighborsRegression, self).__init__(n_iter, shuffle, embedded, seed)
    self.method = method
    self.nearest_neighbor_num = nearest_neighbor_num
    self.hash_num = hash_num

  def _launch_regression(self):
    if self.method in ('euclid_lsh', 'lsh', 'minhash'):
      self.config_ = Config(method='NN', parameter={'method': self.method,
                                                    'nearest_neighbor_num': self.nearest_neighbor_num,
                                                    'parameter': {'hash_num': self.hash_num}})
    elif self.method in ('euclidean', 'cosine'):
      self.config_ = Config(method=self.method,
                            parameter={'nearest_neighbor_num': self.nearest_neighbor_num})
    else:
      raise NotImplementedError('method {} is not implememented yet.'.format(self.method))
    self.regression_ = Regression.run(config=self.config_, embedded=self.embedded)

  def get_params(self, deep=True):
    return {
      'method': self.method,
      'nearest_neighbor_num': self.nearest_neighbor_num,
      'hash_num': self.hash_num,
      'n_iter': self.n_iter,
      'shuffle': self.shuffle,
      'softmax': self.softmax,
      'embedded': self.embedded,
      'seed': self.seed
    }
