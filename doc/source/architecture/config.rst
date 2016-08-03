Config
======

Config defines machine learning parameters and feature extraction rules of Service.

Data Structure
--------------

Config classes inherits ``dict`` class.
Here is an default Config contents for Classifier Service.

.. code-block:: python

  >>> from jubakit.classifier import Config
  >>> cfg = Config()
  >>> print(cfg)
  {'converter': {'string_filter_rules': [], 'num_filter_types': {}, 'num_types': {}, 'num_filter_rules': [], 'string_rules': [{'global_weight': 'idf', 'sample_weight': 'tf', 'key': '*', 'type': 'unigram'}], 'string_filter_types': {}, 'num_rules': [{'key': '*', 'type': 'num'}], 'binary_types': {}, 'binary_rules': [], 'string_types': {'bigram': {'method': 'ngram', 'char_num': '2'}, 'trigram': {'method': 'ngram', 'char_num': '3'}, 'unigram': {'method': 'ngram', 'char_num': '1'}}}, 'method': 'AROW', 'parameter': {'regularization_weight': 1.0}}

The data structure is same as the Jubatus servers' JSON configuration file.
See the `Jubatus API Reference <http://jubat.us/en/api.html>`_ for details.

Machine Learning Parameters
---------------------------

Machine learning parameters are consist of Methods and Hyper Parameters.
Parameters that works well in most cases are set to Config class by default, so you can start using machine learning features without configuring them.

You can create Config instance using these parameters specified.

.. code-block:: python

  >>> from jubakit.classifier import Config
  >>> cfg = Config(method='PA', parameter={'regularization_weight': 1.0})

If you only specify ``method``, the default parameter for the specified method will be set automatically.

.. code-block:: python

  >>> cfg = Config(method='NN')
  >>> cfg['parameter']
  {'local_sensitivity': 1.0, 'nearest_neighbor_num': 128, 'parameter': {'threads': -1, 'hash_num': 64}, 'method': 'euclid_lsh'}
  >>> cfg = Config(method='NHERD')
  >>> cfg['parameter']
  {'regularization_weight': 1.0}

You can even modify parameters after creating Config instance as if it is a ``dict`` object.

.. code-block:: python

  >>> print(cfg['method'])
  AROW
  >>> print(cfg['parameter']['regularization_weight'])
  1.0
  >>> cfg['method'] = 'NHERD'
  >>> cfg['parameter']['regularization_weight'] = 0.1

Feature Extraction Rules
------------------------

The default feature extraction rules are as follows:

* String features are processed with ``unigram`` with TF-IDF weighting.
  For convenience ``bigram`` and ``trigram`` are also defined in ``string_types`` by default.
* Numeric features are processed as is (using ``num`` type).
* Binary features are not processed.

You can clear these default rules by calling ``clear_converter`` method.
It is convenient when writing rules from scratch.

.. code-block:: python

  >>> cfg.clear_converter()
  >>> cfg
  {'converter': {'string_filter_rules': [], 'num_filter_types': {}, 'num_types': {}, 'num_filter_rules': [], 'string_rules': [], 'string_filter_types': {}, 'num_rules': [], 'binary_types': {}, 'binary_rules': [], 'string_types': {}}, 'method': 'AROW', 'parameter': {'regularization_weight': 1.0}}
