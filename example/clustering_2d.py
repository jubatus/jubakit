#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Using Clustering
========================================

This is a simple example that illustrates Clustering service usage.

"""

from jubakit.clustering import Clustering, Schema, Dataset, Config
from jubakit.loader.csv import CSVLoader

# Load a CSV file.
loader = CSVLoader('blobs.csv')

# Define a Schema that defines types for each columns of the CSV file.
schema = Schema({
  'cluster': Schema.ID,
}, Schema.NUMBER)

# Create a Dataset.
dataset = Dataset(loader, schema)

# Create an Clustering Service.
cfg = Config(method='kmeans')
clustering = Clustering.run(cfg)

# Update the Clustering model.
for (idx, row_id, result) in clustering.push(dataset):
  pass

# Get clusters
clusters = clustering.get_core_members(light=False)
# Get centers of each cluster
centers = clustering.get_k_center()

# Calculate SSE: sum of squared errors
sse = 0.0
for cluster, center in zip(clusters, centers):
  # Center of clusters
  center = {"x1": center.num_values[0][1], "x2": center.num_values[1][1]}
  for d in cluster:
    vector = d.point.num_values
    x1 = [x[1] for x in vector if x[0] == 'x1'][0]
    x2 = [x[1] for x in vector if x[0] == 'x2'][0]
    sse += (x1 - center["x1"])**2 + (x2- center["x2"])**2
print('SSE:', sse)

clustering.stop()
