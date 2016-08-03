Schema
======

Schema defines the meaning of each column of record loaded from Loader.
The basic usage of Schema is to specify data types for each key one by one.
In the following example, ``name`` and ``age`` columns are used as features and ``gender`` column is used as a label when training classifier.

.. code-block:: python

  from jubakit.classifier import Schema

  schema = Schema({
    'name': Schema.STRING,
    'age': Schema.NUMBER,
    'gender': Schema.LABEL,
  })

Fallback Type
-------------

Data types must be defined for all column keys that may input from Loader.
If you have many columns in your data and only a part of the columns is of your interest, you can specify a fallback data type.
The Schema in the following example ignores columns other than ``name``, ``age`` and ``gender``.

.. code-block:: python

  schema = Schema({
    'name': Schema.STRING,
    'age': Schema.NUMBER,
    'gender': Schema.LABEL,
  }, Schema.IGNORE)

Similarly, if you know that all of your records are numeric feature, you can just specify Schema as follows using fallback data type.

.. code-block:: python

  schema = Schema({}, Schema.NUMBER)

Alias Names
-----------

By default, the column key names passed from Loader is used as a Datum key name.
However, you can manually assign the Datum key name by giving alias names.
In the following example, ``user_name`` and ``user_profile`` columns will become ``name`` and ``profile`` in Datum respectively.

.. code-block:: python

  schema = Schema({
    'user_name': (Schema.STRING, 'name'),
    'user_profile': (Schema.STRING, 'profile'),
  })

Alias names are convenient when training records from multiple data sources that have different Schema into one Service.

List of Data Types
------------------

Following data types can be specified for Schema.

+---------------+-----------------------------------------------------------------------+
| Type          | Description                                                           |
+===============+=======================================================================+
| ``NUMBER``    | Feature (numeric)                                                     |
+---------------+-----------------------------------------------------------------------+
| ``STRING``    | Feature (string)                                                      |
+---------------+-----------------------------------------------------------------------+
| ``BINARY``    | Feature (binary)                                                      |
+---------------+-----------------------------------------------------------------------+
| ``INFER``     | Feature (infer data type automatically [1]_)                          |
+---------------+-----------------------------------------------------------------------+
| ``AUTO``      | Feature (use data type loaded by Loader [2]_)                         |
+---------------+-----------------------------------------------------------------------+
| ``LABEL``     | Ground truth (label column) -- Classifier only                        |
+---------------+-----------------------------------------------------------------------+
| ``FLAG``      | Flag if the record is anomaly or not -- Anomaly only                  |
+---------------+-----------------------------------------------------------------------+
| ``ID``        | Key that uniquely identifies each record -- Anomaly only              |
+---------------+-----------------------------------------------------------------------+
| ``IGNORE``    | Discard the column                                                    |
+---------------+-----------------------------------------------------------------------+

.. [1] Each data is tried to be cast to  ``NUMBER``, ``STRING`` and ``BINARY``, and treated as that type once cast succeeds.
       Type will be estimated for every single record, so be aware that result of type inference for the same key may different between records.
.. [2] ``AUTO`` is intended to be used with Loader that loads records from typed data sources like RDBMS.
       Note that all data will become STRING when using :py:class:`CSVLoader <jubakit.loader.csv.CSVLoader>` as CSV files is not typed data source.
