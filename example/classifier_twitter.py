#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Using Classifier and Twitter Streaming Loader
=============================================

This example illustrates how to train/classify tweets from Twitter streams.

To run this example, ``tweepy`` and ``jq`` package is required.
You can install them by ``pip install tweepy jq``.
"""

from jubakit.classifier import Classifier, Schema, Dataset, Config
from jubakit.loader.twitter import TwitterStreamLoader, TwitterOAuthHandler

def get_loader():
  # Creates a Twitter stream loader.
  # Fill in your keys here;  you can get keys at: https://apps.twitter.com/
  return TwitterStreamLoader(TwitterOAuthHandler(
    consumer_key='XXXXXXXXXXXXXXXXXXXX',
    consumer_secret='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    access_token='XXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    access_secret='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
  ))

# Define a Schema.
schema = Schema({
  '.lang': Schema.LABEL,
  '.text': Schema.STRING,
  '.user.lang': Schema.STRING,
  '.user.description': Schema.STRING,
}, Schema.IGNORE)

# Create a Classifier Service.
classifier = Classifier.run(Config())

# Number of tweets used for training.
n_train = 1000

print('---- Train: {0} tweets -------------------------------------'.format(n_train))

# Train the classifier using tweets from Twitter stream.
trained_labels = set()
dataset = Dataset(get_loader(), schema)
for (idx, label) in classifier.train(dataset):
  if idx == n_train: break

  trained_labels.add(label)
  text_summary = dataset.get(idx)['.text'].replace('\n', '')
  print('Train[{0}]: language {1}  >> {2}'.format(idx, label, text_summary))

print('Languages Trained: {0}'.format(str(trained_labels)))

print('---- Prediction (Ctrl-C to stop) -------------------------------------')

try:
  # Classify tweets using the classifier.
  (y_true, y_pred) = ([], [])
  dataset = Dataset(get_loader(), schema)
  for (idx, label, result) in classifier.classify(dataset):
    (true_lang, pred_lang) = (label, result[0][0])
    text_summary = dataset.get(idx)['.text'].replace('\n', '')

    message = None
    if pred_lang == true_lang:
      message = 'correct!'
    elif true_lang in trained_labels:
      message = 'incorrect'
    else:
      # The correct language is what we haven't trained.
      message = 'not-trained'

    print("Classify[{0}]: {1} (predicted = {2} | actual = {3})  >> {4}".format(idx, message, pred_lang, true_lang, text_summary))

    if true_lang in trained_labels:
      y_true.append(true_lang)
      y_pred.append(pred_lang)

except KeyboardInterrupt:
  pass  # Trap Ctrl-C

try:
  # If scikit-learn is available, display metrics.
  import sklearn.metrics
  print(sklearn.metrics.classification_report(y_true, y_pred))
except ImportError:
  pass
