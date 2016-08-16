#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Using Recommender
========================================

This is a simple example that illustrates Recommender service usage.

"""

from jubakit.recommender import Recommender, Schema, Dataset, Config
from jubakit.loader.csv import CSVLoader

# Load a CSV file.
loader = CSVLoader('npb.csv')

# Define a Schema that defines types for each columns of the CSV file.
schema = Schema({
  'name': Schema.ID,
  'team': Schema.STRING,
}, Schema.NUMBER)

# Create a Dataset.
dataset = Dataset(loader, schema)

# Create an Recommender Service.
cfg = Config(method='lsh')
recommender = Recommender.run(cfg)

# Update the Recommender model.
for (idx, row_id, success) in recommender.update_row(dataset):
  pass

# Calculate the similarity in recommender model from row-id and display top-2 similar items.
print('{0}\n recommend similar players from row-id \n{1}'.format('-'*60, '-'*60))
for (idx, row_id, result) in recommender.similar_row_from_id(dataset, size=3):
  if idx % 10 == 0:
    print('player {0} is similar to : {1} (score:{2:.3f}), {3} (score:{4:.3f})'.format(
          result[0].id, result[1].id, result[1].score, result[2].id, result[2].score))

# Define a Schema without `name`.
schema = Schema({
  'name': Schema.IGNORE,
  'team': Schema.STRING,    
}, Schema.NUMBER)

# Create the dataset.
dataset = Dataset(loader, schema)

# Calculate the similarity in recommender model from datum and display top-2 similar items.
print('{0}\n recommend similar players from datum \n{1}'.format('-'*60, '-'*60))
for (idx, row_id, result) in recommender.similar_row_from_datum(dataset, size=3):
  if idx % 10 == 0:
    print('player {0} is similar to : {1} (score:{2:.3f}), {3} (score:{4:.3f})'.format(
          result[0].id, result[1].id, result[1].score, result[2].id, result[2].score))

# Stop the Recommender Service.
recommender.stop()

