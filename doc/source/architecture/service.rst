Service
=======

Service makes update/analyze RPC calls to Jubatus servers for each record in Dataset and returns the result.

API
---

Service classes generally provide APIs that have the same name as the `Jubatus RPC API <http://jubat.us/en/api/index.html>`_.
These APIs takes Dataset as an argument.

In addition to machine learning APIs, Service classes provide ``clear``, ``save``, ``load`` and ``get_status`` APIs.

Process Invocation
------------------

Service classes can launch Jubatus server processes.
The following example runs ``jubaclassifier`` process with the default configuration.

.. code-block:: python

  from jubakit.classifier import Config, Classifier

  # Create a default configuration.
  cfg = Config()

  # Start the server process.
  classifier_service = Classifier.run(cfg)

  # ... do some train/classify tasks ...

  # Stop the classifier process and return logs.
  classifier_service.stop()

The server process will run in the standalone mode.
A TCP port that does not conflict with other processes will be picked and assigned automatically.
Once the Service instance (``classifier_service``) got out of focus, the server process will be terminated by the destructor.

Working with External Jubatus
-----------------------------

Jubakit can even be used with externally managed Jubatus processes.

.. code-block:: python

  from jubakit.classifier import Classifier

  # Classifier Service connects to ``127.0.0.1:9199`` using cluster name ``my_cluster``.
  classifier_service = Classifier('127.0.0.1', 9199, 'my_cluster')

  # ... do some train/classify tasks ...

Embedded Jubatus
----------------

Jubakit can use "embedded" version of Jubatus as a backend, which reduces the cost of process invocation and RPC overhead.

.. code-block:: python

  from jubakit.classifier import Config, Classifier

  # Create a default configuration.
  cfg = Config()

  # Create a new service in "Embedded" mode.
  classifier_service = Classifier.run(cfg, embedded=True)

  # ... do some train/classify tasks ...

To use "embedded" feature, ``embedded_jubatus`` ([embedded-jubatus-python](https://github.com/jubatus/embedded-jubatus-python)) Python module, which is a wrapper module to call machine learning algorithms provided in Jubatus Core library, needs to be installed.

List of Services
----------------

Currently the following Services are available in Jubakit.

* `Classifier <http://jubat.us/en/api/api_classifier.html>`_ -- :py:class:`jubakit.classifier.Classifier`
* `Anomaly <http://jubat.us/en/api/api_anomaly.html>`_ -- :py:class:`jubakit.anomaly.Anomaly`
* `Recommender <http://jubat.us/en/api/api_recommender.html>`_ -- :py:class:`jubakit.recommender.Recommender`
* `Weight <http://jubat.us/en/api/api_weight.html>`_ -- :py:class:`jubakit.weight.Weight`

Support of other Services is ongoing.
