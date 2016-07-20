#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Hyperparameter Optimization with Hyperopt
===================================================

In this example, we show how to tune hyperparameters with
Hyperopt bayesian optimization library.

To run this example, ``hyperopt``, ``pymongo`` and ``networkx`` is required.

* for python2 users, install them using `pip` commands.
    
    $ pip install pymongo networkx hyperopt

* for python3 users, install them using `python setup.py install` commands.

    $ pip install git+https://github.com/hyperopt/hyperopt.git

"""

import numpy as np

import sklearn.datasets
from sklearn.metrics import accuracy_score
from sklearn.cross_validation import StratifiedKFold

from hyperopt import fmin, tpe, hp, rand

from jubakit.classifier import Classifier, Dataset, Config

# hyperparameter domains 
classifier_types = ['LinearClassifier', 'NearestNeighbor']
# linear classifier hyperparameters
linear_methods = ['AROW', 'CW']
regularization_weight = [0.0001, 1000.0] 
# nearest neighbor classifier hyperparameters
nn_methods = ['lsh', 'euclid_lsh', 'minhash']
nearest_neighbor_num = [2, 100]
local_sensitivity = [0.01, 10]
hash_num = [512, 512] 

def search_space():
  """
  Return hyperparameter space with Hyperopt format.
  References: https://github.com/hyperopt/hyperopt/wiki/FMin
  """
  space = hp.choice('classifier_type', [
      {
         'classifier_type': 'LinearClassifier',
         'linear_method': hp.choice('linear_method', linear_methods),
         'regularization_weight': hp.loguniform('regularization_weight',
                                            np.log(regularization_weight[0]), 
                                            np.log(regularization_weight[1]))
      }, {
         'classifier_type': 'NearestNeighbor',
         'nn_method': hp.choice('nn_method', nn_methods),
         'nearest_neighbor_num': hp.uniform('nearest_neighbor_num', 
                                            nearest_neighbor_num[0], 
                                            nearest_neighbor_num[1]),
         'local_sensitivity': hp.loguniform('local_sensitivity', 
                                            np.log(local_sensitivity[0]), 
                                            np.log(local_sensitivity[1])),
         'hash_num': hp.loguniform('hash_num', np.log(hash_num[0]), np.log(hash_num[1]))
      }
  ])
  
  return space


def jubatus_config(params):
  """
  convert hyperopt config to jubatus config
  """
  if params['classifier_type'] == 'LinearClassifier':
    config = Config(method=params['linear_method'], 
    	            parameter={'regularization_weight': params['regularization_weight']})

  elif params['classifier_type'] == 'NearestNeighbor':
    config = Config(method='NN',
                    parameter={'method': params['nn_method'],
                               'nearest_neighbor_num': int(params['nearest_neighbor_num']),
                               'local_sensitivity': params['local_sensitivity'],
                               'parameter': {'hash_num': int(params['hash_num'])}})

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
  # print score and hyperparameters
  print_log(score, params)
  # hyperopt only minimize target function and we convert the accuracy score to be minimized.
  return -1.0 * score


def print_log(score, params): 
  """
  Print tuning processes.
  """  
  if params['classifier_type'] == 'LinearClassifier':
    msg = ' {0:.4f}: {1:<5} (reguralization_weight:{0:.4f})'.format(
              score, params['linear_method'], params['regularization_weight'])
  elif params['classifier_type'] == 'NearestNeighbor':
    msg = ' {0:.4f}: {1:<5} (method:{2}, nearest_neighbor_num:{3}, local_sensitivity:{4:.4f}, hash_num:{5})'.format(
              score, 'NN', params['nn_method'], int(params['nearest_neighbor_num']), 
              params['local_sensitivity'], int(params['hash_num']))
  else:
    raise NotImplementedError()
  print(msg)


def print_result(params): 
  """
  Print best score and its hyperparameters.
  """  
  params['classifier_type'] = classifier_types[params['classifier_type']]
  if params['classifier_type'] == 'LinearClassifier':
    params['linear_method'] = linear_methods[params['linear_method']]
  elif params['classifier_type'] == 'NearestNeighbor':
    params['nn_method'] = nn_methods[params['nn_method']]
  else:
    raise NotImplementedError()
  print(' {}\n {}\n {}'.format('-'*60, 'best score and hyperparameters', '-'*60))
  function(params)


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
  # print tuning process header
  print(' {0:<6}: {1:<5} ({2})'.format('score', 'algo', 'hyperparameters'))
  # minimize the target function to be minimized
  best = fmin(function, space, algo=algo, max_evals=max_evals)
  # print result
  print_result(best)
