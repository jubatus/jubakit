# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import socket
import optparse

import msgpackrpc
import jubatus

from .compat import *
from ._stdio import print, get_stdio
from ._cli.base import BaseCLI, CLIInvalidatedException, CLIUnknownCommandException

class JubaShell(object):
  """
  JubaShell provides a shell environment to call Jubatus RPC API.

  The interactive interface is provided in ``cli`` submodule.
  """

  # Default shell prompt format.
  _PS = '[Jubatus:{service}<{cluster}>@{host}:{port}] # '

  # Cached references for CLI classes.
  _cli_classes = {}

  # Cached references for Jubatus Client classes.
  _client_classes = {}

  # Error message.
  _INTERFACE_MISMATCH_ERROR = \
    'Interface mismatch error detected.  ' \
    'This error occured because either your version of Jubatus Python ' \
    'client library is not compatible with the server you are ' \
    'connecting to, or using an incompatible shell (for example, ' \
    'using Classifier shell against Anomaly server.)\n' \
    'Version compatibility information can be found at:\n' \
    '  https://github.com/jubatus/jubatus/wiki/Client-Compatibility-and-Documentation'

  def __init__(self, host, port, cluster, service, **kwargs):
    """
    Creates a new shell environment using parameters specified.

    If ``service`` is ``None``, it will be automatically probed.
    """
    self._host = host
    self._port = port
    self._cluster = cluster
    self._service = None

    self._client = None
    self._timeout = kwargs.get('timeout', 10)
    self._keepalive = kwargs.get('keepalive', False)
    self._verbose = kwargs.get('verbose', False)
    self._prompt_format = kwargs.get('prompt', self._PS)
    self._input = kwargs.get('input', None)
    self._output = kwargs.get('output', get_stdio()[1])  # stdout

    self.set_remote(host, port, cluster, service)

  def interact(self):
    """
    Starts the interactive shell environment.
    """
    cli = self._new_cli()
    while True:
      try:
        self.connect()
        cli.cmdloop()
        return True
      except CLIInvalidatedException:
        cli = self._new_cli()
      except CLIUnknownCommandException as e:
        print('Unknown command: {0}'.format(e))
        print('Type `help` for commands available.')
      except ValueError as e:
        print('Invalid argument: {0}; use `help` command for details'.format(e))
      except socket.gaierror as e:
        print('Socket Error ({0}:{1}): {2} ({3})'.format(self._host, self._port, type(e).__name__, e))
      except msgpackrpc.error.RPCError as e:
        print('RPC Error ({0}:{1}): {2} ({3})'.format(self._host, self._port, type(e).__name__, e))
      except JubaShellException as e:
        print('Error: {0} ({1})'.format(type(e).__name__, e))
      except KeyboardInterrupt:  # trap Ctrl-C
        print()
      except jubatus.common.client.InterfaceMismatch as e:
        print('RPC Interface Mismatch ({0}:{1}): {2}'.format(self._host, self._port, e))
        print(self._INTERFACE_MISMATCH_ERROR)
        break  # abort interactive shell
      finally:
        self.disconnect()
    return False

  def run(self, command):
    """
    Runs one-shot command.
    """
    cli = self._new_cli()
    try:
      self.connect()
      print('>> {0}'.format(command))
      cli.onecmd(command)
      return True
    except CLIInvalidatedException:
      cli = self._new_cli()
      return True
    except CLIUnknownCommandException as e:
      print('Unknown command: {0}'.format(e))
    except ValueError as e:
      print('Invalid argument: {0}'.format(e))
    except socket.gaierror as e:
      print('Socket Error ({0}:{1}): {2} ({3})'.format(self._host, self._port, type(e).__name__, e))
    except msgpackrpc.error.RPCError as e:
      print('RPC Error ({0}:{1}): {2} ({3})'.format(self._host, self._port, type(e).__name__, e))
    except JubaShellException as e:
      print('Error: {0} ({1})'.format(type(e).__name__, e))
    except KeyboardInterrupt:  # trap Ctrl-C
      print('Interrupted.')
    except jubatus.common.client.InterfaceMismatch as e:
      print('RPC Interface Mismatch ({0}:{1}): {2}'.format(self._host, self._port, e))
      print(self._INTERFACE_MISMATCH_ERROR)
    finally:
      self.disconnect()
    return False

  def connect(self):
    """
    Discard the current connection (if connected) and create new client instance.
    Note that TCP connection will not be established until RPC method is called.
    """
    self.disconnect()
    self._client = self._new_client()

  def disconnect(self):
    """
    Disconnects from the server (if connected).
    """
    if self.is_connected():
      cli = self._client.get_client()
      cli.close()
      cli._loop._ioloop.close()
      self._client = None

  def is_connected(self):
    """
    Returns True if the client exists.
    Note that its backend TCP connection may already be closed.
    """
    return self._client is not None

  def set_remote(self, host, port, cluster, service):
    """
    Switches to the new remote server.
    """
    self.disconnect()

    self._host = host
    self._port = port
    self._cluster = cluster

    if service is None:
      service = self.probe_facts(host, port, cluster)[0]

    self._service = service

  def get_client(self):
    """
    Returns the client instance.
    """
    if not self.is_connected():
      self.connect()
    return self._client

  def get_timeout(self):
    """
    Returns the current client-side timeout value.
    """
    return self._timeout

  def set_timeout(self, timeout):
    """
    Sets new client-side timeout value.
    Existing connection will be discarded.
    """
    self.disconnect()
    self._timeout = timeout

  def _new_client(self):
    """
    Returns new Jubatus client instance.
    """
    service = self._service
    clients = self.get_client_classes()
    if service not in clients:
      print('Notice: Jubatus Client for {0} service not found, falling back to generic client'.format(service))
      service = 'generic'

    return clients[service](self._host, self._port, self._cluster, self._timeout)

  def _new_cli(self):
    """
    Returns new CLI instance.
    """
    service = self._service
    clis = self.get_cli_classes()
    if service not in clis:
      print('Notice: CLI for {0} service not found, falling back to generic CLI'.format(service))
      service = 'generic'

    cli = clis[service](self, stdin=self._input, stdout=self._output)
    if self._input:
      cli.use_rawinput = False
    cli.prompt = self._prompt_format.format(
      service=self._service,
      host=self._host,
      port=self._port,
      cluster=self._cluster,
    )

    return cli

  @classmethod
  def probe_facts(cls, host, port, cluster):
    """
    Probe the service name and remote server type.
    Returns tuple of (service_name, is_proxy).
    """
    # Get status from remote server.
    client = jubatus.common.client.ClientBase(host, port, cluster, 0)
    status = None
    is_proxy = bool(cluster)  # only when cluster is non-empty string

    try:
      if is_proxy:
        try:
          results = client.get_proxy_status()
          if len(results) != 1:
            raise JubaShellAssertionError('unexpected get_proxy_status response', host, port, cluster, results)
          status = results.popitem()[1]
        except jubatus.common.client.UnknownMethod:
          is_proxy = False
      if not is_proxy:
        results = client.get_status()
        if len(results) == 0:
          raise JubaShellAssertionError('unexpected get_status response', host, port, cluster, results)
        status = results.popitem()[1]
    except msgpackrpc.error.RPCError as e:
      raise JubaShellRPCError('failed to auto-detect service type', host, port, e)
    finally:
      cli = client.get_client()
      cli.close()
      cli._loop._ioloop.close()

    # Extract service name from the process name.
    if not 'PROGNAME' in status:
      raise JubaShellAssertionError('no program name returned from server', host, port, cluster, status)
    service = status['PROGNAME']
    if service.startswith('juba'):
      service = service[4:]
    if is_proxy and service.endswith('_proxy'):
      service = service[:-6]

    return (service, is_proxy)

  @classmethod
  def _get_subclasses(cls, clazz):
    """
    Finds all subclasses of the ``clazz``.
    """
    result = set()
    queue = [clazz]
    while queue:
      parent = queue.pop()
      for child in parent.__subclasses__():
        if child not in result:
          result.add(child)
          queue.append(child)
    return result

  @classmethod
  def get_client_classes(cls):
    """
    Returns map of service name to Jubatus client instance.
    """
    # Reuse cache.
    clients = cls._client_classes
    if len(clients) != 0:
      return clients

    client_classes = cls._get_subclasses(jubatus.common.client.ClientBase)
    for clazz in client_classes:
      # Extract "abc" part from "jubatus.abc.client" (module name).
      name = clazz.__module__.split('.')[-2]
      clients[name] = clazz

    clients['generic'] = jubatus.common.client.ClientBase

    cls._clients = clients
    return clients

  @classmethod
  def get_cli_classes(cls):
    """
    Returns map of service name to CLI implementation class.
    """
    # Reuse cache.
    clis = cls._cli_classes
    if len(clis) != 0:
      return clis

    cli_classes = cls._get_subclasses(BaseCLI)
    for clazz in cli_classes:
      try:
        name = clazz._name()
        clis[name] = clazz
      except NotImplementedError:  # it is an abstract class
        continue

    cls._clis = clis
    return clis

class JubaShellException(Exception):
  pass

class JubaShellAssertionError(JubaShellException):
  pass

class JubaShellRPCError(JubaShellException):
  def __init__(self, msg, host, port, e=None):
    errmsg = 'RPC Error ({0}:{1}): {2}'.format(host, port, msg)
    if e:
      errmsg += ' ({0}: {1})'.format(type(e).__name__, str(e))
    super(JubaShellRPCError, self).__init__(errmsg)

class JubashOptionParser(optparse.OptionParser, object):
  def __init__(self, *args, **kwargs):
    self._error = False
    super(JubashOptionParser, self).__init__(*args, **kwargs)

  def error(self, msg):
    print('Error: {0}'.format(msg))
    self._error = True

class JubashCommand(object):
  """
  Provides command line interface for ``jubash`` command.
  """

  @classmethod
  def start(cls, args):
    USAGE = '''
    jubash [--host HOST] [--port PORT] [--cluster CLUSTER]
           [--service SERVICE] [--command COMMAND]
           [--keepalive] [--fail-fast] [--prompt PROMPT]
           [--verbose] [--debug] [--help] [script ...]'''
    EPILOG = '  script ...            execute shell script instead of interactive shell'

    services = sorted(JubaShell.get_cli_classes().keys())

    # TODO: migrate to argparse (which must be added into dependency to support Python 2.6)
    parser = JubashOptionParser(add_help_option=False, usage=USAGE, epilog=EPILOG)

    parser.add_option('-H', '--host', type='string', default='127.0.0.1',
                      help='host name or IP address of the server / proxy (default: %default)')
    parser.add_option('-P', '--port', type='int',  default=9199,
                      help='port number of the server / proxy (default: %default)')
    parser.add_option('-C', '--cluster', type='string', default='',
                      help='cluster name; only required when connecting to proxy')
    parser.add_option('-s', '--service', type='string', default=None,
                      help='type of the server; see below for services available (default: auto-detect)')
    parser.add_option('-e', '--engine', type='string', default=None,
                      help='(deprecated) equivalent to --service')
    parser.add_option('-c', '--command', type='string', default=None,
                      help='run one-shot command instead of interactive shell')
    parser.add_option('-t', '--timeout', type='int', default=10,
                      help='client-side timeout in seconds (default: %default)')
    parser.add_option('-k', '--keepalive', default=False, action='store_true',
                      help='use keep-alive connection; recommended when server-side timeout is disabled')
    parser.add_option('-F', '--fail-fast', default=False, action='store_true',
                      help='exit on error when running script')
    parser.add_option('-p', '--prompt', type='string', default=JubaShell._PS,
                      help='use customized shell prompt (default: %default)')
    parser.add_option('-v', '--verbose', default=False, action='store_true',
                      help='turn on verbose mode')
    parser.add_option('-d', '--debug', default=False, action='store_true',
                      help='turn on debug mode')
    parser.add_option('-h', '--help', default=False, action='store_true',
                      help='print the usage and exit')

    def print_usage():
      print('Jubash - Jubatus Shell')
      print()
      parser.print_help(get_stdio()[1])  # stdout
      print()
      print('Available Services:')
      print('  {0}'.format(', '.join(services)))

    (args, scripts) = parser.parse_args(args)

    # Failed to parse options.
    if parser._error:
      print_usage()
      return 2

    # Help option is specified.
    if args.help:
      print_usage()
      return 0

    # Support for deprecated parameters.
    if args.service is None:
      args.service = args.engine

    # Validate parameters.
    if args.port < 1 or 65535 < args.port:
      print('Error: port number out of range: {0}'.format(args.port))
      print_usage()
      return 1
    if args.service is not None and args.service not in services:
      print('Error: unknown service name: {0}'.format(args.service))
      print_usage()
      return 1

    success = False
    try:
      # Create shell instance.
      shell = JubaShell(
        host=args.host,
        port=args.port,
        cluster=args.cluster,
        service=args.service,
        timeout=args.timeout,
        keepalive=args.keepalive,
        verbose=args.verbose,
        prompt=args.prompt,
      )

      # Run the shell.
      if args.command:
        # One-shot command mode.
        success = shell.run(args.command)
      elif len(scripts) != 0:
        # Batch script mode.
        for script in scripts:
          success = True
          # TODO improve handling of lines and support keepalive mode
          for line in open(script, 'r'):
            line = line.rstrip()
            if line and not line.startswith('#'):
              success = shell.run(line)
              if not success and args.fail_fast: break
      else:
        # Interactive shell mode.
        success = shell.interact()
    except Exception as e:
      if args.debug: raise
      print('{0}: {1}'.format(type(e).__name__, e))

    return 0 if success else 3

def main():
  """
  Entry point for ``jubash`` command.
  """
  sys.exit(JubashCommand.start(sys.argv[1:]))
