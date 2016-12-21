#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Grid Search with scikit-learn
=============================

In this example, we show how to use scikit-learn wrapper.

"""

import sklearn
from operator import itemgetter
from jubakit.wrapper import LinearClassifier, NearestNeighborsClassifier
from sklearn.datasets import load_digits
from sklearn.utils import shuffle
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
# switch GridSearchCV API 
sklearn_version = int(sklearn.__version__.split('.')[1])
if sklearn_version < 18:
    from sklearn.grid_search import GridSearchCV
else:
    from sklearn.model_selection import GridSearchCV

# Grid Search parameters
param_grid = {
    'method': ['euclid_lsh', 'lsh'],
    'nearest_neighbor_num': [4, 8, 16, 32],
    'local_sensitivity':  [0.1, 1.0, 10],
}

# Sample dataset
digits = load_digits()
X, y = shuffle(digits.data, digits.target)

# Launch Nearest Neighbor Classifier
clf = NearestNeighborsClassifier(embedded=False, hash_num=128)

# Execute Grid Search
grid_search = GridSearchCV(clf, cv=4, n_jobs=-1, param_grid=param_grid, verbose=2)
grid_search.fit(X, y)

# Output the results.
if sklearn_version < 18:
    grid_scores = sorted(grid_search.grid_scores_, key=itemgetter(1), reverse=True)
    for i, score in enumerate(grid_scores):
        print('Rank:{0}\tScore:{1:.3f}\tParameter:{2}'.format(
               i+1, score.mean_validation_score, score.parameters))
else:
    means = grid_search.cv_results_['mean_test_score']
    params = grid_search.cv_results_['params']
    grid_scores = sorted([(mean, param) for mean, param in zip(means, params)], key=itemgetter(0), reverse=True)
    for i, grid_score in enumerate(grid_scores):
        print('Rank:{0}\tScore:{1:.3f}\tParameter:{2}'.format(
              i+1, grid_score[0], grid_score[1]))
        
