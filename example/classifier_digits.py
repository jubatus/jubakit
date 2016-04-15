#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# Create a Classifier Service
cfg = Config(method='AROW', parameter={'regularization_weight': 0.1})
classifier = Classifier.run(cfg)

# Train the classifier using the first half of the dataset.
print("Training...")
train_ds = dataset[:n_samples / 2]
for _ in classifier.train(train_ds): pass

# Test the classifier using the last half of the dataset.
print("Testing...")
y_true = []
y_pred = []
for (idx, label, result) in classifier.classify(dataset[n_samples / 2:]):
  y_true.append(label)
  y_pred.append(result[0][0])

# Print the result.
print(sklearn.metrics.classification_report(y_true, y_pred))
