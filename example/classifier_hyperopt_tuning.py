#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Hyperparameter Optimization with Hyperopt
===================================================

In this example, we show how to tune hyperparameters with
Hyperopt bayesian optimization library.

If you don't have Hyperopt, please install using following command.
	
	pip install hyperopt 

"""

import numpy as np

import sklearn.datasets
from sklearn.metrics import accuracy_score
from sklearn.cross_validation import StratifiedKFold

from hyperopt import fmin, tpe, hp, rand

from jubakit.classifier import Classifier, Dataset, Config


def search_space():
  """
  Return hyperparameter space with Hyperopt format.
  References: https://github.com/hyperopt/hyperopt/wiki/FMin
  """
  space = hp.choice('classifier_type', [
      {
         'type': 'NearestNeighbor',
         'method': hp.choice('nn_method', ['lsh', 'euclid_lsh', 'minhash']),
         'nearest_neighbor_num': hp.uniform('nearest_neighbor_num', 2, 100),
         'local_sensitivity': hp.loguniform('local_sensitivity', np.log(0.01), np.log(10)),
         'hash_num': 512,
      },
      {
         'type': 'LinearClassifier',
         'method': hp.choice('linear_method', ['AROW', 'CW']),
         'regularization_weight': hp.loguniform('regularization_weight',
                                            np.log(0.0001), np.log(1000.0))
      }
  ])
  
  return space


def jubatus_config(params):
  """
  convert hyperopt config to jubatus config
  """
  if params['type'] == 'NearestNeighbor':
    config = Config(method='NN',
                    parameter={'method': params['method'],
                               'nearest_neighbor_num': int(params['nearest_neighbor_num']),
                               'local_sensitivity': params['local_sensitivity'],
                               'parameter': {'hash_num': int(params['hash_num'])}})

  elif params['type'] == 'LinearClassifier':
    config = Config(method=params['method'], 
    	            parameter={'regularization_weight': params['regularization_weight']})

  else:
  	raise NotImplementedError()

  return config


def cv_score(classifier, dataset, metric=accuracy_score, n_folds=10):
  """
  Calculate K-fold cross validation score.
  """  
  true_labels = []
  predicted_labels = []
  for train_idx, test_idx in StratifiedKFold(list(dataset.get_labels()), n_folds=n_folds):
    # clear the classifier (call `clear` RPC).
    classifier.clear()
    
    # split the dataset to train/test dataset.
    (train_ds, test_ds) = (dataset[train_idx], dataset[test_idx])

    # train the classifier using train dataset.
    for (idx, label) in classifier.train(train_ds):
      pass
    
    # test the classifier using test dataset.
    for (idx, label, result) in classifier.classify(test_ds):     
      # labels are already desc sorted by score values, so you can get a label
      # name with the hightest prediction score by:
      pred_label = result[0][0]

      # store the result.
      true_labels.append(label)
      predicted_labels.append(pred_label)

  # return cross-validation score
  return metric(true_labels, predicted_labels)


def function(params):
  """
  Function to be optimized.
  """
  # generate config
  config = jubatus_config(params)
  # create a classifier service.
  classifier = Classifier.run(config)
  # scoring metric (default accuracy metric)
  metric = accuracy_score
  # calculate cross-validation score
  score = cv_score(classifier, dataset, metric=metric)
  # stop the classifier
  classifier.stop()
  # print result
  # print('{0:<10}\t{1:.3f}\t\t{2:.3f}'.format(method, rw, score))
  print('score: {}'.format(score))
  print('\tparams:{}'.format(params))
  # hyperopt only minimize target function and we convert the accuracy score to be minimized.
  return -1.0 * score


if __name__ == '__main__':
  # load built-in `iris` dataset from scikit-learn.
  iris = sklearn.datasets.load_iris()
  # convert it into jubakit Dataset.
  dataset = Dataset.from_array(iris.data, iris.target, iris.feature_names, iris.target_names)
  # shuffle the dataset because the dataset is sorted by labels.
  dataset = dataset.shuffle()
  # obtain hyperparameter search space.
  space = search_space()
  # select the optimization strategy
  # we can use bayesian optimizer `tpe.suggest` or random optimizer `rand.suggest`
  algo = tpe.suggest
  # set the evaluation count.
  # in this example, cross-validation function `cv_score` runs `max_evals` times.
  max_evals = 10
  # minimize the target function to be minimized
  best = fmin(function, space, algo=algo, max_evals=max_evals)
  # print result
  print('best estimated parameters')
  print('\t{}'.format(best))
