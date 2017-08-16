#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Using Clustering
========================================

This is a simple example that illustrates Clustering service usage.

"""

import collections
from sklearn.datasets import make_blobs

from jubakit.wrapper.clustering import KMeans, GMM, DBSCAN

# make blob dataset using sklearn API.
X, y = make_blobs(n_samples=200, centers=3, n_features=2, random_state=42)

# launch clustering instance
clusterings = [
    KMeans(k=3, bucket_size=200, embedded=False),
    GMM(k=3, bucket_size=200, embedded=False),
    DBSCAN(eps=2.0, bucket_size=200, embedded=False)
]

for clustering in clusterings:
    # fit and predict
    y_pred = clustering.fit_predict(X)
    # print result
    print('{0}: {1}'.format(
           clustering.__class__.__name__,
           collections.Counter(y_pred)))
    # stop clustering service
    clustering.stop()

