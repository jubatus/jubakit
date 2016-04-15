#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Using Classifier and String Features
========================================

This is a famous `shogun` classifier example that predicts family name
of Shogun from his first name.
"""

from jubakit.classifier import Classifier, Schema, Dataset, Config
from jubakit.loader.csv import CSVLoader

# Load the shogun dataset.
train_loader = CSVLoader('shogun.train.csv')
test_loader = CSVLoader('shogun.test.csv')

# Define a Schema that defines types for each columns of the CSV file.
schema = Schema({
  'family_name': Schema.LABEL,
  'first_name': Schema.STRING,
})

# Create a Dataset.
train_dataset = Dataset(train_loader, schema).shuffle()
test_dataset = Dataset(test_loader, schema)

# Create a Classifier Service.
cfg = Config(
  method = 'PA',
  converter = {
    'string_rules': [{'key': 'first_name', 'type': 'unigram', 'sample_weight': 'bin', 'global_weight': 'bin'}]
  }
)
classifier = Classifier.run(cfg)

# Train the classifier.
for _ in classifier.train(train_dataset): pass

# Classify using the classifier.
for (idx, label, result) in classifier.classify(test_dataset):
  true_family_name = label
  pred_family_name = result[0][0]
  first_name = test_dataset.get(idx)['first_name']
  print("{0} {1} ({2})".format(
    pred_family_name,
    first_name,
    'correct!' if pred_family_name == true_family_name else 'incorrect'
  ))

# Stop the classifier.
classifier.stop()
