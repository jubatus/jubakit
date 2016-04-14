# -*- coding: utf-8 -*-

import sklearn.metrics as skm
import numpy as np

from ..compat import *

def accuracy_score(y_true, y_pred, *args, **kwargs):
  (y_true, y_pred, _) = _map_labels_to_numeric(y_true, y_pred)
  return skm.accuracy_score(y_true, y_pred, *args, **kwargs)

def precision_score(y_true, y_pred, *args, **kwargs):
  (y_true, y_pred, _) = _map_labels_to_numeric(y_true, y_pred)
  return skm.precision_score(y_true, y_pred, *args, **kwargs)

def f1_score(y_true, y_pred, *args, **kwargs):
  (y_true, y_pred, _) = _map_labels_to_numeric(y_true, y_pred)
  return skm.f1_score(y_true, y_pred, *args, **kwargs)

def classification_report(y_true, y_pred, *args, **kwargs):
  (y_true, y_pred, labels) = _map_labels_to_numeric(y_true, y_pred)
  return skm.classification_report(y_true, y_pred, np.arange(len(labels)), labels, *args, **kwargs)

def _map_labels_to_numeric(true_labels, pred_labels=[]):
  # Make labels into string.
  true_labels = map(unicode_t, true_labels)
  pred_labels = map(unicode_t, pred_labels)

  # Replace string labels with numeric label.
  labels = list(set(true_labels + pred_labels))
  labelmap = dict(zip(labels, range(len(labels))))

  y_true = np.array([labelmap[x] for x in true_labels])
  y_pred = np.array([labelmap[x] for x in pred_labels])

  return (y_true, y_pred, labels)
