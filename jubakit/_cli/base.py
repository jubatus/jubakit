# -*- ncoding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import subprocess

from .._stdio import print
from .cmd import ExtendedCmd
from .args import Arguments, Optional

class BaseCLI(ExtendedCmd):
  """
  A base class for CLI interface of all services.
  """

  def __init__(self, shell, *args, **kwargs):
    super(BaseCLI, self).__init__(*args, **kwargs)

    self._sh = shell

    # Set help sentences.
    self.doc_header = "Commands:"
    self.undoc_header = "Commands (no help available):"
    self.misc_header = "Documents:"
    self.nohelp = "No help available for %s."

    # Register aliases.
    self.register_alias('EOF', 'do_exit')
    self.register_alias('ls', 'do_help')
    self.register_alias('shell', 'shell_command')

  #################################################################
  # Override methods to tweak CLI behavior
  #################################################################

  def emptyline(self):
    """
    By default, empty line causes the previous command to run again.
    This overrides the default handler for emptyline so it behaves like an usual shell.
    """
    pass

  def postcmd(self, stop, line):
    """
    After a single command is executed, we discard the connection if not in
    keepalive mode.
    """
    if not self._sh._keepalive:
      self._sh.disconnect()
      self._sh.connect()
    return stop

  def default(self, line):
    """
    Raise exception for unhandled commands.
    """
    raise CLIUnknownCommandException(line)

  #################################################################
  # Common interfaces for Jubatus CLI
  #################################################################

  @classmethod
  def _name(cls):
    """
    Returns the name of the service (e.g., `classifier`).
    You must override this in subclasses.
    """
    raise NotImplementedError

  def _verbose(self, msg):
    """
    Outputs logs only when in verbose mode.
    """
    if self._sh._verbose:
      print(msg)

  @property
  def client(self):
    """
    Returns the client instance.
    """
    return self._sh.get_client()

  #################################################################
  # Built-in shell commands
  #################################################################

  @Arguments()
  def do_exit(self):
    """Syntax: exit
    Exits the shell.  You can also use EOF (Ctrl-D).
    """
    print()
    return True

  def help_help(self):
    print(
    """Syntax: help [command]
    Displays the list of commands available.
    If ``command`` is specified, displays the help for the command."""
    )

  def shell_command(self, param):
    """
    Runs the command in the *real* shell.
    """
    subprocess.call(param, shell=True)

class CLIInvalidatedException(Exception):
  """
  Notify Shell to regenerate CLI instance.
  """
  pass

class CLIUnknownCommandException(Exception):
  """
  Notify Shell that unknown command is specified.
  """
  pass

class BaseRpcCLI(BaseCLI):
  """
  CLI that supports RPC commands.
  """

  @Arguments(str, int, Optional(str))
  def do_connect(self, host, port, cluster):
    """Syntax: connect host port [cluster]
    Connect to the specified host, port and cluster (optional).
    """
    if cluster is None:
      cluster = self._sh._cluster

    print("Connecting to <{0}>@{1}:{2}...".format(cluster, host, port))
    self._sh.set_remote(host, port, cluster, None)
    raise CLIInvalidatedException()

  @Arguments()
  def do_reconnect(self):
    """Syntax: reconnect
    Reconnects to the current server.
    """
    self._sh.connect()
    raise CLIInvalidatedException()

  @Arguments()
  def do_verbose(self):
    """Syntax: verbose
    Toggles the verbose mode.
    """
    self._sh._verbose = not self._sh._verbose
    if self._sh._verbose:
      print("Verbose mode: on")
    else:
      print("Verbose mode: off")

  @Arguments()
  def do_keepalive(self):
    """Syntax: keepalive
    Toggles the keepalive mode.
    """
    self._sh._keepalive = not self._sh._keepalive
    if self._sh._keepalive:
      print("Keepalive: enabled")
    else:
      print("Keepalive: disabled")

  @Arguments(Optional(int))
  def do_timeout(self, timeout):
    """Syntax: timeout [new_value]
    Displays or sets the client-side timeout.
    """
    if timeout is not None:
      self._sh.set_timeout(timeout)
    print("Timeout: {0} seconds".format(self._sh.get_timeout()))
