Jubamodel Reference
===================

Synopsis
--------------------------------------------------

.. code-block:: shell

  jubamodel [--in-format IN_FORMAT] [--out-format OUT_FORMAT]
            [--output OUTPUT] [--output-config OUTPUT_CONFIG]
            [--no-validate] [--fix-header] [--help]  model_file

Description
--------------------------------------------------

``jubamodel`` is a command line utility to perform low-level manipulation of model files.
If you are wishing for high-level, user friendly output of models, use ``jubadump`` command instead.
Unlike ``jubadump``, ``jubamodel`` is service-independent; you can use ``jubamodel`` for any services.

The binary model data structure is documented in `Jubatus Wiki <https://github.com/jubatus/jubatus/wiki/Save-and-Load-Policy-(ja)>`_ (in Japanese).

Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``[]`` indicates the default value.

.. program:: jubamodel

.. option:: -i <format>, --in-format <format>

   Format of the input model file.  [``auto``]

   The format can be any of ``auto`` (default), ``binary`` or ``json``.
   ``auto`` automatically predicts the model format from the file specified.
   ``binary`` is a model format that can be loaded by Jubatus server.
   ``json`` is a model format that can be loaded by ``jubamodel`` command.

.. option:: -o <format>, --out-format <format>

   Format of the output model file.  [``text``]

   The format can be any of ``text`` (default), ``binary`` or ``json``.
   ``text`` is a user-friendly output of the model file.
   See :option:`--in-format` for ``binary`` and ``json``.

.. option:: -O <output>, --output <output>

   Path to the output file.
   When specified, the result will be written to the file instead of the standard output.
   This option is mandatory if you specify ``binary`` to :option:`--out-format`.

.. option:: -C <output_config>, --output-config <output_config>

   Path to the output config file.
   When specified, Jubatus configuration (JSON) will be extracted from the model and written to the specified file.

.. option:: -f, --no-validate

   When loading model files in ``binary`` format, ``jubamodel`` validates the model data structure (including CRC32 checksum).
   When this option is specified, the validation will be disabled.

.. option:: -F, --fix-header

   When this option is specified, the model data structure will be fixed.
   See the example section for details.

.. option:: -h, --help

   Show the usage of the command.


Examples
--------------------------------------------------

You can see the meta data of the model file using ``jubamodel``:

::

  $ jubamodel /tmp/127.0.0.1_9199_classifier_test.jubatus

To convert the binary model into JSON format:

::

  $ jubamodel -o json -O /tmp/model.json /tmp/127.0.0.1_9199_classifier_test.jubatus

Once converted into JSON format, you can manually modify the JSON file.
You can then convert the modified JSON model back to the binary model; note the ``-F`` option, which recomputes CRC32 checksum and other system data.

::

  $ jubamodel -fF -o binary -O /tmp/127.0.0.1_9199_classifier_test2.jubatus /tmp/model.json
