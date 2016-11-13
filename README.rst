|Travis|_ |Coveralls|_ |PyPi|_

.. |Travis| image:: https://api.travis-ci.org/jubatus/jubakit.svg?branch=master
.. _Travis: https://travis-ci.org/jubatus/jubakit

.. |Coveralls| image:: https://coveralls.io/repos/jubatus/jubakit/badge.svg?branch=master&service=github
.. _Coveralls: https://coveralls.io/r/jubatus/jubakit

.. |PyPi| image:: https://badge.fury.io/py/jubakit.svg
.. _PyPi: https://badge.fury.io/py/jubakit

jubakit: Jubatus Toolkit
========================

jubakit is a Python module to access Jubatus features easily.
jubakit can be used in conjunction with `scikit-learn <http://scikit-learn.org/>`_ so that you can use powerful features like cross validation and model evaluation.
See the `Jubakit Documentation <http://jubat.us/en/jubakit>`_ for the detailed description.

Currently jubakit supports `Classifier <http://jubat.us/en/api_classifier.html>`_, `Anomaly <http://jubat.us/en/api_anomaly.html>`_, `Recommender <http://jubat.us/en/api_recommender.html>`_ and `Weight <http://jubat.us/en/api_weight.html>`_ engines.

Install
-------

::

  pip install jubakit

Requirements
------------

* Python 2.6, 2.7, 3.3, 3.4 or 3.5.
* `Jubatus <http://jubat.us/en/quickstart.html>`_ needs to be installed.
* Although not mandatory, `installing scikit-learn <http://scikit-learn.org/stable/install.html>`_ is required to use some features like K-fold cross validation.

Quick Start
-----------

The following example shows how to perform train/classify using CSV dataset.

.. code:: python

  from jubakit.classifier import Classifier, Schema, Dataset, Config
  from jubakit.loader.csv import CSVLoader

  # Load a CSV file.
  loader = CSVLoader('iris.csv')

  # Define types for each column in the CSV file.
  schema = Schema({
    'Species': Schema.LABEL,
  }, Schema.NUMBER)

  # Get the shuffled dataset.
  dataset = Dataset(loader, schema).shuffle()

  # Run the classifier service (`jubaclassifier` process).
  classifier = Classifier.run(Config())

  # Train the classifier.
  for _ in classifier.train(dataset): pass

  # Classify using the trained classifier.
  for (idx, label, result) in classifier.classify(dataset):
    print("true label: {0}, estimated label: {1}".format(label, result[0][0]))

Examples by Topics
------------------

See the `example <https://github.com/jubatus/jubakit/tree/master/example>`_ directory for working examples.

+-----------------------------------+-----------------------------------------------+-----------------------+
| Example                           | Topics                                        | Requires scikit-learn |
+===================================+===============================================+=======================+
| classifier_csv.py                 | Handling CSV file and numeric features        |                       |
+-----------------------------------+-----------------------------------------------+-----------------------+
| classifier_shogun.py              | Handling CSV file and string features         |                       |
+-----------------------------------+-----------------------------------------------+-----------------------+
| classifier_digits.py              | Handling toy dataset (digits)                 | ✓                     |
+-----------------------------------+-----------------------------------------------+-----------------------+
| classifier_libsvm.py              | Handling LIBSVM file                          | ✓                     |
+-----------------------------------+-----------------------------------------------+-----------------------+
| classifier_kfold.py               | K-fold cross validation and metrics           | ✓                     |
+-----------------------------------+-----------------------------------------------+-----------------------+
| classifier_parameter.py           | Finding best hyper parameter                  | ✓                     |
+-----------------------------------+-----------------------------------------------+-----------------------+
| classifier_hyperopt_tuning.py     | Finding best hyper parameter using hyperopt   | ✓                     |
+-----------------------------------+-----------------------------------------------+-----------------------+
| classifier_bulk.py                | Bulk Train-Test Classifier                    |                       |
+-----------------------------------+-----------------------------------------------+-----------------------+
| classifier_twitter.py             | Handling Twitter Streams                      |                       |
+-----------------------------------+-----------------------------------------------+-----------------------+
| anomaly_auc.py                    | Anomaly detection and metrics                 |                       |
+-----------------------------------+-----------------------------------------------+-----------------------+
| recommender_npb.py                | Recommend similar items                       |                       |
+-----------------------------------+-----------------------------------------------+-----------------------+
| weight_shogun.py                  | Tracing fv_converter behavior using Weight    |                       |
+-----------------------------------+-----------------------------------------------+-----------------------+
| weight_model_extract.py           | Extract contents of Weight model file         |                       |
+-----------------------------------+-----------------------------------------------+-----------------------+

License
-------

MIT License
