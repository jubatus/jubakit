# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from ..classifier import Classifier, Config, Dataset


class BaseJubatusClassifier(BaseEstimator, ClassifierMixin):
  """
  scikit-learn Wrapper for Jubatus Classifiers.
  """

  def __init__(self, n_iter=1, shuffle=False, softmax=False, embedded=True, seed=None):
    """
    Creates a base class for Jubatus Classifiers.
    """
    self.softmax = softmax
    self.n_iter = n_iter
    self.shuffle = shuffle
    self.embedded = embedded
    self.seed = seed

  @classmethod
  def _launch_classifier(self):
    """
    Launch Jubatus Classifier
    """
    raise NotImplementedError()

  def partial_fit(self, X, y):
    """
    Partially fit underlying model.
    If underlying model does not exist, launch a new model.
    """
    if getattr(self, 'classes_', None) is None:
      self.classes_ = np.unique(y)
    if getattr(self, 'classifier_', None) is None:
      self._launch_classifier()
      self.classifier_.clear()
    dataset = Dataset.from_data(X, y)
    for i in range(self.n_iter):
      if self.shuffle:
        dataset = dataset.shuffle(self.seed)
      for _ in self.classifier_.train(dataset): pass
    return self

  def fit(self, X, y):
    """
    Fit model.
    """
    self._launch_classifier()
    self.classifier_.clear()
    return self.partial_fit(X, y)

  def predict(self, X):
    """
    Predict class labels for samples in X.
    """
    if getattr(self, 'classifier_', None) is None:
      raise RuntimeError('This estimator instance is not fitted yet.')
    y_pred = np.empty(X.shape[0], dtype=self.classes_.dtype)
    dataset = Dataset.from_data(X)
    for idx, _, result in self.classifier_.classify(dataset, softmax=self.softmax):
      y_pred[idx] = result[0][0]
    return y_pred

  def decision_function(self, X):
    """
    Predict confidence scores for samples.
    """
    if getattr(self, 'classifier_', None) is None:
      raise RuntimeError('This estimator instance is not fitted yet.')
    scores = np.empty((X.shape[0], len(self.classes_)))
    dataset = Dataset.from_data(X)
    for idx, _, result in self.classifier_.classify(dataset, softmax=self.softmax):
      for (label, score) in result:
        scores[idx][np.searchsorted(self.classes_, label)] = score
    return scores

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
    Save the classifier model using name.
    """
    if self.classifier_ is not None:
      self.classifier_.save(name)

  def stop(self):
    """
    Stop the backend process if exists.
    """
    if not self.embedded and self.classifier_ is not None:
      self.classifier_.stop()
      self.classifier_ = None


class LinearClassifier(BaseJubatusClassifier):

  def __init__(self, method='AROW', regularization_weight=1.0,
               softmax=False, n_iter=1, shuffle=False, embedded=True, seed=None):
    super(LinearClassifier, self).__init__(n_iter, shuffle, softmax, embedded, seed)
    self.method = method
    self.regularization_weight = regularization_weight

  def _launch_classifier(self):
    if self.method in ('perceptron', 'PA'):
      self.config_ = Config(method=self.method)
    elif self.method in ('PA1', 'PA2', 'CW', 'AROW', 'NHERD'):
      self.config_ = Config(method=self.method,
                            parameter={'regularization_weight': self.regularization_weight})
    else:
      raise NotImplementedError('method {} is not implemented yet.'.format(self.method))
    self.classifier_ = Classifier.run(config=self.config_, embedded=self.embedded)

  def get_params(self, deep=True):
    return {
      'method': self.method,
      'regularization_weight': self.regularization_weight,
      'n_iter': self.n_iter,
      'shuffle': self.shuffle,
      'softmax': self.softmax,
      'embedded': self.embedded,
      'seed': self.seed
    }


class NearestNeighborsClassifier(BaseJubatusClassifier):

  def __init__(self, method='euclid_lsh', nearest_neighbor_num=5, local_sensitivity=1.0,
               hash_num=128, n_iter=1, shuffle=False, softmax=False, embedded=True, seed=None):
    super(NearestNeighborsClassifier, self).__init__(n_iter, shuffle, softmax, embedded, seed)
    self.method = method
    self.nearest_neighbor_num = nearest_neighbor_num
    self.local_sensitivity = local_sensitivity
    self.hash_num = hash_num

  def _launch_classifier(self):
    if self.method in ('euclid_lsh', 'lsh', 'minhash'):
      self.config_ = Config(method='NN', parameter={'method': self.method,
                                                    'nearest_neighbor_num': self.nearest_neighbor_num,
                                                    'local_sensitivity': self.local_sensitivity,
                                                    'parameter': {'hash_num': self.hash_num}})
    elif self.method in ('euclidean', 'cosine'):
      self.config_ = Config(method=self.method,
                            parameter={'nearest_neighbor_num': self.nearest_neighbor_num,
                                       'local_sensitivity': self.local_sensitivity})
    else:
      raise NotImplementedError('method {} is not implemented yet.'.format(self.method))
    self.classifier_ = Classifier.run(config=self.config_, embedded=self.embedded)

  def get_params(self, deep=True):
    return {
      'method': self.method,
      'nearest_neighbor_num': self.nearest_neighbor_num,
      'local_sensitivity': self.local_sensitivity,
      'hash_num': self.hash_num,
      'n_iter': self.n_iter,
      'shuffle': self.shuffle,
      'softmax': self.softmax,
      'embedded': self.embedded,
      'seed': self.seed
    }
