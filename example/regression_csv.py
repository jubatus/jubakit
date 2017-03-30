#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Using Regression and Boston dataset
==================================================

In this example we show regression using Boston dataset.
"""

import numpy as np
from jubakit.regression import Regression, Schema, Dataset, Config
from jubakit.loader.csv import CSVLoader

# Load a CSV file.
loader = CSVLoader('wine.csv')

# Define a Schema that defines types for each columns of the CSV file.
schema = Schema({
  'quality': Schema.TARGET,
}, Schema.NUMBER)

# Create a Dataset
dataset = Dataset(loader, schema).shuffle()
n_samples = len(dataset)
n_train_samples = int(n_samples * 0.75)

# Create a Regression Service
cfg = Config.default()
regression = Regression.run(cfg)

print("Started Service: {0}".format(regression))

# Train the regression using the first half of the dataset.
train_ds = dataset[:n_train_samples]
print("Training...: {0}".format(train_ds))
for _ in regression.train(train_ds): pass

# Test the regression using the last half of the dataset.
test_ds = dataset[n_train_samples:]
print("Testing...: {0}".format(test_ds))
mse, mae = 0, 0
for (idx, label, result) in regression.estimate(test_ds):
  diff = np.abs(label - result)
  mse += diff**2
  mae += diff
mse /= len(test_ds)
mae /= len(test_ds)

# Stop the regression.
regression.stop()

# Print the result
print('Root Mean Squared Error: {0:.3f}'.format(np.sqrt(mse)))
print('Mean Absolute Error: {0:.3f}'.format(mae))
