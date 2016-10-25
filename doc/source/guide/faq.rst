Frequently Asked Questions
==========================

* How can I debug Jubakit script?
    * Jubakit has a built-in logging feature.
      By default, logging is turned off.
      You can enable logging by setting the environment variable like ``export JUBAKIT_LOG_LEVEL=DEBUG`` or adding the following two lines to your code:

.. code-block:: python

  import jubakit.logger
  jubakit.logger.setup_logger(jubakit.logger.DEBUG)

