#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Using Classifier and Digits dataset
===================================================

In this example we show classification using Digits dataset.
"""

import sklearn.datasets
import sklearn.metrics

import jubakit
from jubakit.classifier import Classifier, Dataset, Config

# Load the digits dataset.
digits = sklearn.datasets.load_digits()

# Create a Dataset.
dataset = Dataset.from_array(digits.data, digits.target)
n_samples = len(dataset)
n_train_samples = int(n_samples / 2)

# Create a Classifier Service
cfg = Config(method='AROW', parameter={'regularization_weight': 0.1})
classifier = Classifier.run(cfg)

print("Started Service: {0}".format(classifier))

# Train the classifier using the first half of the dataset.
train_ds = dataset[:n_train_samples]
print("Training...: {0}".format(train_ds))
for _ in classifier.train(train_ds): pass

# Test the classifier using the last half of the dataset.
test_ds = dataset[n_train_samples:]
print("Testing...: {0}".format(test_ds))
y_true = []
y_pred = []
for (idx, label, result) in classifier.classify(test_ds):
  y_true.append(label)
  y_pred.append(result[0][0])

# Stop the classifier.
classifier.stop()

# Print the result.
print(sklearn.metrics.classification_report(y_true, y_pred))
