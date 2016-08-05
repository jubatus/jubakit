# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json

from ..base import BaseRpcCLI
from ..args import Arguments
from ..util import *

class GenericCLI(BaseRpcCLI):
  """
  Base CLI implementation for all other services.
  """

  def __init__(self, *args, **kwargs):
    super(GenericCLI, self).__init__(*args, **kwargs)
    self._clear_cache()

  @classmethod
  def _name(cls):
    return 'generic'

  def _clear_cache(self):
    """
    Subclasses using cache must override this method; initialize or invalidate
    cache when this method is called.
    """
    pass

  def _print_status(self, status):
    """
    Pretty-print the status structure.
    """
    for (host_port, status) in status.items():
      print("Server {0}:{1}".format(*(host_port.split('_'))))
      for key in sorted(status.keys()):
        print("  {0}: {1}".format(key, status[key]))

  @Arguments()
  def do_get_config(self):
    """Syntax: get_config
    Display algorithm and converter configuration set in server.
    """
    config = self.client.get_config()
    print(json.dumps(json.loads(config), sort_keys=True, indent=4))

  @Arguments(str)
  def do_save(self, model_id):
    """Syntax: save model_id
    Save the model.
    """
    result = self.client.save(model_id)
    if result:
      for (server_id, path) in result.items():
        print("{0}:\t{1}".format(server_id, path))
    else:
      print("Failed")

  @Arguments()
  def do_clear(self):
    """Syntax: clear
    Clear the model.
    """
    result = self.client.clear()
    if not result:
      print("Failed")
    self._clear_cache()

  @Arguments(str)
  def do_load(self, model_id):
    """Syntax: load model_id
    Load the given model.
    """
    result = self.client.load(model_id)
    if not result:
      print("Failed")

  @Arguments()
  def do_get_status(self):
    """Syntax: get_status
    Displays status of servers.
    """
    status = self.client.get_status()
    self._print_status(status)

  @Arguments()
  def do_get_proxy_status(self):
    """Syntax: get_proxy_status
    Displays status of the proxy.
    Available only when connected to proxies.
    """
    status = self.client.get_proxy_status()
    self._print_status(status)

  @Arguments()
  def do_do_mix(self):
    """Syntax: do_mix
    Trigger MIX.
    Available only when connected to servers.
    """
    result = self.client.do_mix()
    if not result:
      print("Failed")
