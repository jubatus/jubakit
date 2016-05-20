#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Using Anomaly and Calculating AUC Score
========================================

This is a simple example that illustrates Anomaly service usage.
"""

from jubakit.anomaly import Anomaly, Schema, Dataset, Config
from jubakit.loader.csv import CSVLoader

# Load a CSV file.
loader = CSVLoader('iris.csv')

# Define a Schema that defines types for each columns of the CSV file.
schema = Schema({
  'Species': Schema.FLAG,
}, Schema.NUMBER)

# Define a function to determine if the record is positive or negative.
# In this example we treat `Iris-virginica` as an "anomaly" record.
def is_positive(x):
  return x == 'Iris-virginica'

# Create a Dataset.
dataset = Dataset(loader, schema)

# Extract the negative (non-anomaly) dataset.
dataset_neg = dataset.convert(lambda data: filter(lambda x: not is_positive(x['Species']), data))

# Create an Anomaly Service.
cfg = Config(parameter={'nearest_neighbor_num': 3})
anomaly = Anomaly.run(cfg)

# Update the anomaly model using negative dataset.
for (idx, row_id, flag, score) in anomaly.add(dataset_neg):
  pass

# Calculate LOF scores for the full dataset.
# It is expected that `Iris-virginica` records get higher scores than others.
y_true = []
y_score = []
for (idx, row_id, flag, score) in anomaly.calc_score(dataset):
  y_true.append(is_positive(flag))
  y_score.append(score)
  print('Score ({0}): {1}'.format(flag, score))

# Stop the Anomaly serivce.
anomaly.stop()

try:
  # If scikit-learn is available, display metrics.
  import sklearn.metrics
  print('-----------------------------')
  print('AUC: {0}'.format(sklearn.metrics.roc_auc_score(y_true, y_score)))
  print('-----------------------------')
  print('Score Threshold and Precision:')
  (fpr, tpr, thresholds) = sklearn.metrics.roc_curve(y_true, y_score)
  for i in range(len(thresholds)):
    print('  Threshold: {0:10.10f} -> True Positive Rate: {1:1.4f}, False Positive Rate: {2:1.4f}'.format(thresholds[i], tpr[i], fpr[i]))
except ImportError:
  print('sklearn is not installed; metrics cannot be calculated')
