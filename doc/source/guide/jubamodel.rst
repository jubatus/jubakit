Jubamodel Reference
===================

Synopsis
--------------------------------------------------

.. code-block:: shell

  jubamodel [--in-format IN_FORMAT] [--out-format OUT_FORMAT]
            [--output OUTPUT] [--output-config OUTPUT_CONFIG]
            [--replace-config REPLACE_CONFIG] [--replace-version REPLACE_VERSION]
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

.. option:: -R <replace_config>, --replace-config <replace_config>

   Path to the configuration file to use.
   When specified, Jubatus configuration (JSON) in the original model file will be overwritten by the contents of the specified file.
   You may also want to specify :option:`--fix-header` together, so that CRC32 checksum and other header values are updated according to the new configuration.

   When using this option, be sure you truly understand what you are doing, as some hyper parameters are not expected to be changed after training models.

.. option:: -Z <replace_version>, --replace-version <replace_version>

   New Jubatus version string (e.g., `1.0.1`) to use.
   When specified, Jubatus version embedded in the model file will be overwritten by the specified version.
   You may also want to specify :option:`--fix-header` together, so that CRC32 checksum and other header values are updated according to the new version.

   Although this may help migrating models between different Jubatus versions, there is no guarantee that the modified model can be loaded to the specified Jubatus version.

.. option:: -f, --no-validate

   When loading model files in ``binary`` format, ``jubamodel`` validates the model data structure (including CRC32 checksum).
   When this option is specified, the validation will be disabled.

.. option:: -F, --fix-header

   When this option is specified, the model data structure is tried to be fixed.
   This includes recomputation of CRC32 checksum and container lengths.

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
You can then convert the modified JSON model back to the binary model; note the :option:`-F` option, which recomputes CRC32 checksum and other system data.

::

  $ jubamodel -fF -o binary -O /tmp/127.0.0.1_9199_classifier_test2.jubatus /tmp/model.json
