Jubash Reference
================

Synopsis
--------------------------------------------------

.. code-block:: shell

  jubash [--host HOST] [--port PORT] [--cluster CLUSTER]
         [--service SERVICE] [--command COMMAND]
         [--keepalive] [--fail-fast] [--prompt PROMPT]
         [--verbose] [--debug] [--help] [script ...]

Description
--------------------------------------------------

``jubash`` is a command line interface to interactively communicate with Jubatus servers.
See :doc:`../architecture/shell` for the detailed description.

Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``[]`` indicates the default value.

.. program:: jubash

.. option:: -H <host>, --host <host>

   Host name or IP address of the server or proxy.  [127.0.0.1]

.. option:: -P <port>, --port <port>

   Port number of the server or proxy.  [9199]

.. option:: -C <cluster>, --cluster <cluster>

   Jubatus cluster name.
   Required when connecting to a proxy.

.. option:: -s <service>, --service <service>

   Name of Jubatus service (``classifier``, ``nearest_neighbor``, etc.)
   Generally you don't have to specify this option; it is auto-detected by default.

.. option:: -e <engine>, --engine <engine>

   Deprecated; equivalent to :option:`--service`.

.. option:: -c <command>, --command <command>

   When specified, run the specified one-shot command instead of starting an interactive shell.

.. option:: -t <timeout>, --timeout <timeout>

   Client side timeout in seconds.  [10]

.. option:: -k, --keepalive

   Use keep-alive connection mode.

   By default, ``jubash`` establishes new TCP connection for each RPC call.
   When this option is specified, ``jubash`` reuses TCP connection.
   Keep-alive mode provides better performance.

   Note that timeout of server or proxy must be disabled (e.g., ``jubaclassifier --timeout 0``) to use keep-alive mode.

.. option:: -F, --fail-fast

   Stop when error occurred when running script.

.. option:: -p <prompt>, --prompt <prompt>

   Use specified shell prompt format in interactive mode.  [``[Jubatus:{service}<{cluster}>@{host}:{port}] #``]

.. option:: -v, --verbose

   Enable verbose mode.
   In verbose mode, the contents of Datum are displayed when making RPC call.

.. option:: -d, --debug

   Enable debug mode.
   In debug mode, stacktrace will be displayed when fatal error occurred.

.. option:: -h, --help

   Show the usage of the command.
