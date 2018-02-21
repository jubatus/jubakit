#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

"""
NearestNeighbor service example.
=================================

This example shows how to use nearest neighbor service.

We use AAAI 2014 Accepted Papers Data Set.

    Lichman, M. (2013).
    UCI Machine Learning Repository [http://archive.ics.uci.edu/ml].
    Irvine, CA: University of California, School of Information and
    Computer Science.

Please download csv file from the url and rename it "aaai.csv"
https://archive.ics.uci.edu/ml/datasets/AAAI+2014+Accepted+Papers
"""

from jubakit.nearest_neighbor import NearestNeighbor, Schema, Dataset, Config
from jubakit.loader.csv import CSVLoader

# Load a CSV file.
loader = CSVLoader('aaai.csv')

# Define a Schema that defines types for each columns of the CSV file.
# In this example, we use "abstract" and "topics" to calculate neighbor scores.
schema = Schema({
    'title': Schema.ID,
    'abstract': Schema.STRING,
    'keyword': Schema.STRING
}, Schema.IGNORE)
print('Schema:', schema)

# Create a Dataset.
dataset = Dataset(loader, schema)

# Create a nearest neighbor configuration.
config = Config()
print(config)

# Launch a nearest neighbor service.
service = NearestNeighbor.run(config)

# add data to nearest neighbor model.
mapper = {}
for (idx, row_id, result) in service.set_row(dataset):
    mapper[row_id] = idx

# search k-neighbor data.
for (idx, row_id, results) in service.neighbor_row_from_id(dataset, size=5):
    print('\n', idx, row_id)
    for r in results[1:]:  # first data is the same as query data.
        print('\tscore: {0:.3f}\ttitle: {1}'.format(r.score, r.id))
