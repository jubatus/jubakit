#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from jubakit.model import JubaDump

"""
Extracting Classifier Models
=============================================

This is an example to show the usage of ``jubakit.model`` package,
which allows low-level model manipulation.

To try this example, first save a model file of jubaclassifier
(hint: ``classifier_csv.py`` example automatically saves the model under /tmp)
Then run this example like:

    $ python classifier_model_extract.py /tmp/127.0.0.1_9199_example_snapshot.jubatus

to see the linear classifier weights, features and labels.
"""

# Load the model from file.
modelpath = 'classifier_iris_model.jubatus'
if 1 < len(sys.argv):
    modelpath = sys.argv[1]

# load the classifier model file.
model = JubaDump.dump_file(modelpath)

# Extract Label Count
print('\n{}\n{}\n{}'.format('-'*50, 'Label Information', '-'*50))
print('Count\tLabel')
label_count = model['storage']['label']['label_count']
for label, count in label_count.items():
    print('{}\t{}'.format(count, label))

# Extract Feature Count
print('\n{}\n{}\n{}'.format('-'*50, 'Feature Information', '-'*50))
print('Count\tFeature')
feature_count = model['weights']['document_frequencies']
for feature, count in feature_count.items():
    print('{}\t{}'.format(count, feature))

# Extract Weight of Linear Classifier
print('\n{}\n{}\n{}'.format('-'*50, 'Weight Information', '-'*50))
weights = model['storage']['storage']['weight']
for feature, label_values in weights.items():
    print('Feature: {}'.format(feature))
    print('\tWeight  \tClass')
    for label, values in label_values.items():
        print('\t{0:+.5f}\t{1}'.format(values['v1'], label))
