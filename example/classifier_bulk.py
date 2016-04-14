#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bulk Train-Test Classifier
========================================

This example uses bulk train-test method of Classifier.
"""

from jubakit.classifier import Classifier, Schema, Dataset, Config
from jubakit.loader.csv import CSVLoader
from jubakit.metrics import classification_report

# Load a CSV file.
loader = CSVLoader('iris.csv')

# Define a Schema that defines types for each columns of the CSV file.
schema = Schema({
  'Species': Schema.LABEL,
}, Schema.NUMBER)

# Create a Dataset.
dataset = Dataset(loader, schema).shuffle()
n_samples = len(dataset)

# Create a Classifier configuration.
cfg = Config()

# Bulk train-test the classifier.
result = Classifier.train_and_classify(
  Config(),
  dataset[:n_samples/2],
  dataset[n_samples/2:],
  classification_report
)

print(result.encode('utf-8'))
