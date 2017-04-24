#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Using Regression and Boston dataset
==================================================

In this example we show regression using Boston dataset.
"""

import numpy as np
import sklearn.datasets
import sklearn.metrics

import jubakit
from jubakit.regression import Regression, Dataset, Config

# Load the boston dataset.
boston = sklearn.datasets.load_boston()
X = boston.data
y = boston.target

# Create a Dataset
dataset = Dataset.from_array(boston.data, boston.target).shuffle()
n_samples = len(dataset)
n_train_samples = int(n_samples * 0.75)

# Create a Regression Service
cfg = Config(method='AROW', parameter={
             'regularization_weight': 1.0, 'sensitivity': 1.0})
regression = Regression.run(cfg)

print("Started Service: {0}".format(regression))

# Train the regression using the first half of the dataset.
train_ds = dataset[:n_train_samples]
print("Training...: {0}".format(train_ds))
for _ in regression.train(train_ds): pass

# Test the regression using the last half of the dataset.
test_ds = dataset[n_train_samples:]
print("Testing...: {0}".format(test_ds))
y_true = []
y_pred = []
for (idx, label, result) in regression.estimate(test_ds):
  y_true.append(label)
  y_pred.append(result)

# Stop the regression.
regression.stop()

# Print the result
rmse = np.sqrt(sklearn.metrics.mean_squared_error(y_true, y_pred))
mae = sklearn.metrics.mean_absolute_error(y_true, y_pred)
print('Root Mean Squared Error: {0:.3f}'.format(rmse))
print('Mean Absolute Error: {0:.3f}'.format(mae))
