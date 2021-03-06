#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

""" 
Pipeline Classification with scikit-learn wrapped Classifier
============================================================

In this example, we show how to use scikit-learn wrapper's 
`fit(X, y)` and `predict(X)` functions. 

"""

from jubakit.wrapper.classifier import LinearClassifier, NearestNeighborsClassifier

from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.utils import shuffle

# load hand-writtern number recognition dataset
digits = load_digits()
# shuffle and separate the dataset
X, y = shuffle(digits.data, digits.target, random_state=42)
n_train = int(X.shape[0] / 2) 
X_train, y_train = X[:n_train], y[:n_train]
X_test, y_test = X[n_train:], y[n_train:]

# launch linear classifier (AROW)
clf = LinearClassifier(method='AROW', embedded=False, seed=42)

# scale dataset 
scaled_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', clf)
])

# decompose dataset
pca_pipeline = Pipeline([
    ('pca', PCA()),
    ('classifier', clf)
])

# evaluate each pipelines
pipelines = [clf, scaled_pipeline, pca_pipeline]
for pipeline in pipelines:
    print(pipeline)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))


