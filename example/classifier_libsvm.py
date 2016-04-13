#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Using Classifier and LIBSVM file
===================================================

In this example we show how to handle LIBSVM file format.
"""

import jubakit
from jubakit.classifier import Classifier, Dataset, Config
import jubakit.metrics

from sklearn.datasets import load_svmlight_files

# Load LIBSVM files.
# Note that these example files are not included in this repository.
# You can fetch them from: https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/multiclass.html#news20
print("Loading LIBSVM files...")
(train_X, train_y, test_X, test_y) = load_svmlight_files(['news20', 'news20.t'])

# Create a Train Dataset.
print("Creating train dataset...")
train_ds = Dataset.from_matrix(train_X, train_y)

# Create a Test Dataset
print("Creating test dataset...")
test_ds = Dataset.from_matrix(test_X, test_y)

# Create a Classifier Service
classifier = Classifier.run(Config())

# Train the classifier.
print("Training...")
for (idx, _) in classifier.train(train_ds):
  if idx % 1000 == 0:
    print("Training... ({0} %)".format(100 * idx / len(train_ds)))

# Test the classifier.
print("Testing...")
y_true = []
y_pred = []
for (idx, label, result) in classifier.classify(test_ds):
  y_true.append(label)
  y_pred.append(result[0][0])
  if idx % 1000 == 0:
    print("Testing... ({0} %)".format(100 * idx / len(test_ds)))

# Print the result.
print(jubakit.metrics.classification_report(y_true, y_pred))
