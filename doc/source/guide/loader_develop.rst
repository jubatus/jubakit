Loader Development Guide
========================

Although Jubakit provides various kinds of built-in Loaders, you can also extend existing Loader or even develop your own one to suit your needs.

Extending Existing Loader
-------------------------

All Loaders have an extension point called ``preprocess``, which is a method you can override and perform operations on each record from the Loader.
``preprocess`` method takes only 1 argument, which is a single record loaded (dict-like object).
The method must return the preprocessed dict-like object or ``None``.

The default implementation of ``preprocess`` method is as follows; it does nothing.

.. code-block:: python

  def preprocess(self, ent):
    return ent

Although not mandatory, the output of ``preprocess`` method should be a flat dict-like object, i.e., values should not be objects.

Transformation
~~~~~~~~~~~~~~

For example, if you want to process JSONL files (files that contain one JSON record per line), you can create a class that inherits from :py:class:`LineBasedFileLoader <jubakit.loader.core.LineBasedFileLoader>` which loads a single text file and emits record for each line, and implement ``preproces`` method as follows:

.. code-block:: python

  import json
  from jubakit.loader.core import LineBasedFileLoader

  class JsonLLoader(LineBasedFileLoader):
    def preprocess(self, ent):
      return json.loads(ent['line'])

Filtering
~~~~~~~~~

You can also use ``preprocess`` method for filtering.
If you want to skip the record, just return ``None``.
The following Loader loads lines whose line number is odd.

.. code-block:: python

  from jubakit.loader.core import LineBasedFileLoader

  class OddLineLoader(LineBasedFileLoader):
    def preprocess(self, ent):
      if ent['number'] % 2 == 0:
        return None
      return ent

Window Processing
~~~~~~~~~~~~~~~~~

As Loaders can be stateful, ``preprocess`` method can also be used for window processing.
Here is an example of Loader that calculates moving average over ``x``.

.. code-block:: python

  from jubakit.base import BaseLoader

  class MovingAverageLoader(BaseLoader):
    def __init__(self, window_size, *args, **kwargs):
      self._window = []
      self._window_size = window_size
      super(MovingAverageLoader, self).__init__(*args, **kwargs)

    def preprocess(self, ent):
      # Window holds the last N records.
      self._window = self._window[-1 * self._window_size + 1:] + [float(ent['x'])]

      # At least N records must be processed.
      if len(self._window) < self._window_size: return None

      # Calculate moving average, add it as a column named `x_avg` and return it.
      ent['x_avg'] = sum(self._window) / self._window_size
      return ent

    def rows(self):
      # Dummy records.
      for x in [1, 10, 5, 8, 7, 6, 2]:
        yield {'x': x}


Implementing New Loader
-----------------------

If none of the existing Loaders didn't work for you, create your own Loader from scratch.
It is quite simple -- the minimum requirements for Loader classes are:

* Loaders must inherit from :py:class:`jubakit.base.BaseLoader` class.
* Loaders must implement ``rows`` method, which yields a ``dict`` object.

Here is a simple example of a Loader, which emits 2-dimensional random number records for 5 times.

.. code-block:: python

  from random import Random
  from jubakit.base import BaseLoader

  class RandomLoader(BaseLoader):
    def rows(self):
      r = Random()
      for i in range(5):
        yield {'x': r.random(), 'y': r.random()}

Loaders can easily be tested as follows.

.. code-block:: python

  >>> loader = RandomLoader()
  >>> for row in loader:
  ...   print(row)
  ...
  {'y': 0.12162269633934364, 'x': 0.005440374791884306}
  {'y': 0.04132353727105431, 'x': 0.12812214533765487}
  {'y': 0.9734068465823698, 'x': 0.35152948844306664}
  {'y': 0.12417565325498592, 'x': 0.7501678925073599}
  {'y': 0.6370897206201418, 'x': 0.01709999005458307}

It is advised to emit flat dict-like object (i.e., no objects in values) in ``rows`` method to avoid confusion.

If you are developing *infinite* Loader (e.g., Twitter streams), it should implement ``is_infinite`` method and return ``True``.
Please note that all entries are loaded from Loader to memory when creating ``Dataset`` by default, unless ``is_infinite`` returns ``True`` (or ``static`` option of ``Dataset`` constructor is explicitly set to ``False``).

.. code-block:: python

  from random import Random
  from jubakit.base import BaseLoader

  class InfiniteRandomLoader(BaseLoader):
    def is_infinite(self):
      return True

    def rows(self):
      r = Random()
      while True:
        yield {'x': r.random(), 'y': r.random()}

Now you need a parameter for your Loader?
You can use a constructor.

.. code-block:: python

  from random import Random
  from jubakit.base import BaseLoader

  class InfiniteRandomLoader(BaseLoader):
    def __init__(self, seed=0):
      self.seed = seed

    def is_infinite(self):
      return True

    def rows(self):
      r = Random(self.seed)
      while True:
        yield {'x': r.random(), 'y': r.random()}

If you wrote a Loader that can be commonly used, please consider submitting `Pull-Request <https://github.com/jubatus/jubakit/pulls>`_ to make the Loader as a part of Jubakit!
