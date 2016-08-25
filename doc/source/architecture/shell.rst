Shell
=====

Shell provides an interactive command line interface, also known as REPL (read-eval-print loop), to communicate with Jubatus servers.

Using REPL from Jubakit Script
------------------------------

The REPL interface can be started from :doc:`service` instances.

.. code-block:: python

  from jubakit.classifier import Classifier, Config
  service = Classifier.run(Config())
  service.shell()

When :py:func:`shell() <jubakit.base.BaseService.shell>` method is called, an interactive shell to control the Service is started.
You can interactively call RPC API to the Jubatus server in the shell.
The jubakit script stops until you exit the shell.

See the next section for the usage of the interactive shell.

Using REPL from Command Line
----------------------------

Jubakit also provides ``jubash`` command, which is a standalone version of the Shell feature.
It can be used as a handy tool to briefly tasting Jubatus without writing code.

When using ``jubash`` command (outside Jubakit script), Jubatus servers needs to be started manually.

.. code::

  $ jubaclassifier -f /usr/share/jubatus/example/config/classifier/default.json &

Now you can connect to the Classifier server using ``jubash``.

.. code::

  $ jubash
  [Jubatus:classifier<>@127.0.0.1:9199] #

The shell prompt appears when connected successfully.
By default, ``jubash`` tries to connect to ``127.0.0.1:9199``.
You can also connect to a remote server and/or a custom port:

.. code::

  $ jubash -H 192.168.1.2 -P 19199

For other options refer to :doc:`../guide/jubash` or ``jubash --help``.

Now you can call any methods defined in `Jubatus RPC API <http://jubat.us/en/api.html>`_ as if it is a command.
For Classifier, you can use ``train`` and ``classify`` command to communicate with Jubatus server interactively.

.. code::

  [Jubatus:classifier<>@127.0.0.1:9199] # train male height 170 weight 60
  [Jubatus:classifier<>@127.0.0.1:9199] # train male height 185 weight 65
  [Jubatus:classifier<>@127.0.0.1:9199] # train female height 150 weight 50
  [Jubatus:classifier<>@127.0.0.1:9199] # train female height 155 weight 45
  [Jubatus:classifier<>@127.0.0.1:9199] # classify height 140 weight 40
  female: 1.0111604929
  male: 0.0962741076946

``train`` method takes the label and the Datum (key-value record) as arguments, whereas ``classify`` method only takes the Datum.
The above example is almost equivalent to the following Python code:

.. code-block:: python

  from jubatus.classifier.client import Classifier
  from jubatus.common import Datum
  from jubatus.classifier.types import LabeledDatum

  client = Classifier('127.0.0.1', 9199, '', 0)

  client.train([LabeledDatum('male', Datum({'height': 170, 'weight': 60}))])
  client.train([LabeledDatum('male', Datum({'height': 185, 'weight': 65}))])
  client.train([LabeledDatum('female', Datum({'height': 150, 'weight': 50}))])
  client.train([LabeledDatum('female', Datum({'height': 155, 'weight': 45}))])

  print(client.classify([Datum({'height': 140, 'weight': 40})]))

``help`` command shows a list of commands available.
If a command name is given to the ``help`` command (like ``help train``), it will show you a brief description of its arguments.

.. code::

  [Jubatus:classifier<>@127.0.0.1:9199] # help

  Commands:
  =========
  classify      do_mix      get_proxy_status  load       timeout
  clear         exit        get_status        reconnect  train
  connect       get_config  help              save       verbose
  delete_label  get_labels  keepalive         set_label

.. code::

  [Jubatus:classifier<>@127.0.0.1:9199] # help train
  Syntax: train label datum_key datum_value [datum_key datum_value ...]
          Trains the model with given label and datum.
          Bulk training is not supported on the command line.

Integrating with Command Line Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also use ``jubash`` to easily integrate Jubatus with your existing command-line workflow or command-based data sources.

You can use ``-c, --command`` option to execute a shell command in batch mode.
For example, you can periodically monitor the status of Jubatus servers like this:

.. code::

  $ watch -n 1 jubash -c get_status

You can also execute ``jubash`` from shell scripts.
The following example illustrates how to call Jubatus API from shell scripts.

.. code-block:: shell

  #!/bin/bash

  # Anomaly detection from number of packets on eth0
  # Note: jubaanomaly must be running on localhost:9199

  NIC="eth0"

  rx() { ifconfig "${NIC}" | perl -n0e 'm/RX bytes:(\d+)/; print $1'; }
  tx() { ifconfig "${NIC}" | perl -n0e 'm/TX bytes:(\d+)/; print $1'; }

  RX2="$(rx)" TX2="$(tx)"
  while :; do
    sleep 1
    RX1="${RX2}" TX1="${TX2}" RX2="$(rx)" TX2="$(tx)"
    jubash -c "add rx $((${RX2} - ${RX1})) tx $((${TX2} - ${TX1}))"
  done

Writing Jubash Script
~~~~~~~~~~~~~~~~~~~~~

As with the usual shell programs, ``jubash`` also works as an interpreter (note the shebang line).

.. code-block:: shell

  #!/usr/local/bin/jubash

  # expecting jubaclassifier is already running on localhost:9199
  connect 127.0.0.1 9199

  get_config
  get_status

  train male height 170 weight 60
  train male height 185 weight 65
  train female height 150 weight 50
  train female height 155 weight 45
  classify height 140 weight 40

Limitations
-----------

Although commands in ``jubash`` are designed to be similar to its corresponding APIs, there are some limitations due to the limit of expression in REPL.

* Types of each data is automatically assumed as float or string.
  The interactive interface is not intended to handle data processing in use cases where strict consistency of data types is required.
* Binary features are not supported.
* Bulk RPC queries (throwing multiple records in single RPC call like ``train`` method of Classifier service) is not supported.
