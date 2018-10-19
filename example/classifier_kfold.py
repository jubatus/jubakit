#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
K-fold Cross Validation and Metrics Calculation
===================================================

In this example we show how to perform K-fold cross validation and
calculate metrics (`classification_report`) using scikit-learn.
"""

import sklearn
import sklearn.datasets
import sklearn.metrics
from jubakit.classifier import Classifier, Dataset, Config

# switch StratifiedKFold API
sklearn_version = int(sklearn.__version__.split('.')[1])
if sklearn_version < 18:
    from sklearn.cross_validation import StratifiedKFold
else:
    from sklearn.model_selection import StratifiedKFold


# Load built-in `iris` dataset from scikit-learn.
iris = sklearn.datasets.load_iris()

# Convert it into jubakit Dataset.
#dataset = Dataset.from_array(iris.data, iris.target)
# ... or, optionally you can assign feature/label names to improve human-readbility.
dataset = Dataset.from_array(iris.data, iris.target, iris.feature_names, iris.target_names)

# Shuffle the dataset, as the dataset is sorted by label.
dataset = dataset.shuffle()

# Create a Classifier Service.
# Classifier process starts using a default configuration.
classifier = Classifier.run(Config())

# Prepare arrays to keep true/predicted labels to display a report later.
true_labels = []
predicted_labels = []

# Run stratified K-fold validation.
labels = list(dataset.get_labels())
if sklearn_version < 18:
    train_test_indices = StratifiedKFold(labels, n_folds=10)
else:
    skf = StratifiedKFold(n_splits=10)
    train_test_indices = skf.split(labels, labels)

for train_idx, test_idx in train_test_indices:
  # Clear the classifier (call `clear` RPC).
  classifier.clear()

  # Split the dataset to train/test dataset.
  (train_ds, test_ds) = (dataset[train_idx], dataset[test_idx])

  # Train the classifier using train dataset.
  for (idx, label) in classifier.train(train_ds):
    # You can peek records being trained.
    #print('train[{0}]: (label: {1}) => {2}'.format(idx, label, train_ds[idx]))
    pass

  # Test the classifier using test dataset.
  for (idx, label, result) in classifier.classify(test_ds):
    # `result` data structure: [ ("label_1", score_1), ("label_2", score_2), ... ]
    # Labels are already desc sorted by score values, so you can get a label
    # name with the hightest prediction score by:
    pred_label = result[0][0]

    # You can peek records being classified.
    #print('classify[{0}]: (true: {1}, predicted: {2}) => {3}'.format(idx, label, pred_label, test_ds[idx]))

    # Store the result.
    true_labels.append(label)
    predicted_labels.append(pred_label)

# Stop the classifier.
classifier.stop()

# Show a classification report.
print(sklearn.metrics.classification_report(true_labels, predicted_labels))
