#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import operator

from jubakit.model import JubaModel

"""
Extracting Model Contents
========================================

This is an example to show the usage of ``jubakit.model`` package,
which allows low-level model manipulation.

To try this example, first save a model file of jubaweight.
(hint: ``weight_shogun.py`` example automatically saves the model under /tmp)
Then run this example like:

  $ python weight_model_extract.py /tmp/127.0.0.1_0000_weight_shogun.jubatus

to see the term frequency of each feature vector.
"""

# Load the model file.
modelpath = 'weight_shogun_model.jubatus'
if 1 < len(sys.argv):
    modelpath = sys.argv[1]

with open(modelpath, 'rb') as f:
    model = JubaModel.load_binary(f)

# Extract the term frequency part of the model data.
weights = model.data()[0][1][1][0]

# Sort features by the term frequency.
sorted_weights = sorted(weights.items(), key=operator.itemgetter(1), reverse=True)

# Print the result.
print("Weight\t\tFeature")
for (k, v) in sorted_weights:
    print("{0}\t\t{1}".format(v, k))
