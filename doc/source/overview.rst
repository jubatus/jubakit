Overview
========

Jubakit is a Python module to access Jubatus features easily.
The goal of Jubakit is to:

* Accerelate cycles of data analysis by integrating powerful scikit-learn features into Jubatus
* Conceal the system architecture of Jubatus (config files, TCP port number assignment, process invocation, RPC call, etc.) to provide an interface that users can focus on data analysis

Here is an shortest example of code using Jubakit.
You can perform anomaly detection on CSV dataset only by 4 lines of Python code:

.. code-block:: python

  dataset = Dataset(CSVLoader("dataset.csv"))
  service = Anomaly.run(Config())
  for result in service.add(dataset):
    print(result)

Jubakit provides a simple-to-use APIs while allowing users to customize detailed behaviors.
Jubakit also comes with configuration parameters that works well in most cases, so you don't have to configure them until necessary.
