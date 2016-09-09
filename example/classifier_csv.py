#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Using Classifier and CSV file
========================================

This is a simple example that illustrates:

* How to load CSV files and convert it into Jubakit dataset.
* Training the classifier using the dataset.
* Getting classification result.
"""

from jubakit.classifier import Classifier, Schema, Dataset, Config
from jubakit.loader.csv import CSVLoader

# Load a CSV file.
loader = CSVLoader('iris.csv')

# Define a Schema that defines types for each columns of the CSV file.
schema = Schema({
  'Species': Schema.LABEL,
  'Sepal.Length': Schema.NUMBER,
  'Sepal.Width': Schema.NUMBER,
  'Petal.Length': Schema.NUMBER,
  'Petal.Width': Schema.NUMBER,
})

# Create a Dataset, which is an abstract representation of a set of data
# that can be fed to Services like Classifier.  `shuffle()` returns a new
# Dataset whose order of data is shuffled.  Note that datasets are immutable
# objects.
dataset = Dataset(loader, schema).shuffle()

# Create a Classifier Service.
# Classifier process starts using a default configuration.
cfg = Config.default()
classifier = Classifier.run(cfg)

# You can also connect to an existing service instead.
#classifier = Classifier('127.0.0.1', 9199)

# Train the classifier with every data in the dataset.
for (idx, label) in classifier.train(dataset):
  # You can peek the datum being trained.
  print("Train: {0}".format(dataset[idx]))

# Save the trained model file.
print("Saving model file...")
classifier.save('example_snapshot')

# Classify using the same dataset.
use_softmax = True
for (idx, label, result) in classifier.classify(dataset, use_softmax):
  print("Classify: {0} (label: {1}, estimated: {2})".format(label == result[0][0], label, result[0][0]))
  for (est_label, est_score) in result:
    print("    Estimated Label: {0} ({1})".format(est_label, est_score))

# Stop the classifier.
classifier.stop()
