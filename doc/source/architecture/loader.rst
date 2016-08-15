Loader
======

Loader fetches data from data sources.
Each Loader class is implemented for its corresponding data source.
For example, you can use :py:class:`CSVLoader <jubakit.loader.csv.CSVLoader>` class to load CSV dataset.

.. code-block:: python

  from jubakit.loader.csv import CSVLoader

  loader = CSVLoader('/path/to/dataset.csv')

The Loader outputs a dict-like (key-value) object for each record loaded from the data source:

.. code-block:: python

  >>> for record in loader:
  ...   print(record)
  {'name': 'John', 'age': '24', 'gender': 'male'}
  {'name': 'Jane', 'age': '35', 'gender': 'female'}
  {'name': 'Mary', 'age': '19', 'gender': 'female'}

List of Loaders
~~~~~~~~~~~~~~~

Loaders for the following data sources are bundled with Jubakit.

* Plain line-based streams and files -- :py:mod:`jubakit.loader.core`
* Array-like (Python lists, NumPy arrays, etc.) data structure -- :py:mod:`jubakit.loader.array`
* SciPy sparse matrix data structure -- :py:mod:`jubakit.loader.sparse`
* CSV files -- :py:mod:`jubakit.loader.csv`
* Twitter streams -- :py:mod:`jubakit.loader.twitter`
* *Chain* Loaders (that wraps other Loaders) -- :py:mod:`jubakit.loader.chain`

You can extend these Loaders or even write your own one.
See :doc:`../guide/loader_develop` for details.
