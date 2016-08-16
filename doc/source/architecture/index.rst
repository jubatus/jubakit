Architecture
============

Here is a brief architecture of Jubakit:

.. image:: /images/architecture.png

There are 6 components that consists of Jubakit:

* :doc:`loader` fetches data from various data sources (e.g., CSV file, RDBMS, MQ, Twitter stream, etc.) in key-value format.
* :doc:`schema` defines the data type (string feature, numeric feature, ground truth (label), etc.) for each keys of data loaded by Loader.
* :doc:`dataset` transforms records loaded from Loader into Jubatus Datum using Schema.  Dataset is an abstract representation of a sequence of data.
* :doc:`service` makes update/analyze RPC calls to Jubatus servers for each record in Dataset and returns the result.
* :doc:`config` defines parameters of Service.
* :doc:`shell` provides an interactive command line interface to communicate with Jubatus servers.

Note that *Schema*, *Dataset* and *Config* are defined for each *Service*.
For example, you must use :py:class:`jubakit.classifier.Schema` for :py:class:`jubakit.classifier.Classifier` service, not :py:class:`jubakit.anomaly.Schema`.

.. toctree::
   :hidden:

   loader
   schema
   dataset
   service
   config
   shell
