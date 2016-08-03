Frequently Asked Questions
==========================

* How can I debug Jubakit script?
    * Jubakit has a built-in logging feature.
      By default logging is turned off.
      To enable logging, add the following two lines to your code:

.. code-block:: python

  import jubakit.logger
  jubakit.logger.setup_logger(jubakit.logger.DEBUG)

