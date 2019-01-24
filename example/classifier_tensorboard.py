#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Visualize training process with TensorBoard
===========================================

In this example, we show the training process of Jubatus with TensorBoard.

TensorBoard syntax is little complicated and in this example we use tensorboardX library.
tensorboardX is a simple wrapper of TensorBoard that write events with simple function call.

[How to Use]

1. Install tensorboard.

    ```
    $ pip install tensorboardX
    ```

2. Run this example.

3. Check the training process using tensorboard.

    ```
    $ tensorboard --logdir runs/***
    ```

4. Enjoy!

"""

from sklearn.datasets import load_digits
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, log_loss)

from tensorboardX import SummaryWriter

import jubakit
from jubakit.classifier import Classifier, Dataset, Config
from jubakit.model import JubaDump

# Load the digits dataset.
digits = load_digits()

# Create a dataset.
dataset = Dataset.from_array(digits.data, digits.target)
n_samples = len(dataset)
n_train_samples = int(n_samples * 0.7)
train_ds = dataset[:n_train_samples]
test_ds = dataset[n_train_samples:]

# Create a classifier.
config = Config(method='AROW',
                parameter={'regularization_weight': 0.1})
classifier = Classifier.run(config)

model_name = 'classifier_digits'
model_path = '/tmp/{}_{}_classifier_{}.jubatus'.format(
    classifier._host, classifier._port, model_name)

# show the feature weights of the target label.
target_label = 4

# Initialize summary writer.
writer = SummaryWriter()

# train and test the classifier.
epochs = 100
for epoch in range(epochs):
    # train
    for _ in classifier.train(train_ds): pass

    # test
    y_true, y_pred = [], []
    for (_, label, result) in classifier.classify(test_ds):
        y_true.append(label)
        y_pred.append(result[0][0])

    # save model to check the feature weights
    classifier.save(model_name)

    model = JubaDump.dump_file(model_path)
    weights = model['storage']['storage']['weight']
    for feature, label_values in weights.items():
        for label, value in label_values.items():
            if str(label) != str(target_label):
                continue
            writer.add_scalar('weights/{}'.format(feature), value['v1'], epoch)

    # write scores to tensorboardX summary writer.
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='macro')
    recall = recall_score(y_true, y_pred, average='macro')
    f1 = f1_score(y_true, y_pred, average='macro')
    writer.add_scalar('metrics/accuracy', acc, epoch)
    writer.add_scalar('metrics/precision', prec, epoch)
    writer.add_scalar('metrics/recall', recall, epoch)
    writer.add_scalar('metrics/f1_score', f1, epoch)

writer.close()
classifier.stop()
