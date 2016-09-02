# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import random
import time
import logging
import subprocess
import os
import platform
import distutils.spawn
import tempfile

import msgpackrpc
import psutil

from .compat import *
from .logger import get_logger

_logger = get_logger()

class JubaProcess(object):
  @classmethod
  def get_process(cls, cmdline, *args, **kwargs):
    """
    Returns subprocess.Popen instance.
    """
    envvars = dict(os.environ)
    if platform.system() == 'Darwin' and 'DYLD_FALLBACK_LIBRARY_PATH' not in envvars:
      """
      Due to homebrew-jubatus issue #15, when using Homebrew with locations other than
      the standard installation path (/usr/local), Jubatus processes built on OS X cannot
      be run without DYLD_FALLBACK_LIBRARY_PATH.  However, on El Capitan or later,
      DYLD_FALLBACK_LIBRARY_PATH are not propagated from parent process.  We workaround
      the problem by automatically estimating DYLD_FALLBACK_LIBRARY_PATH based on PATH.
      """
      cmdpath = distutils.spawn.find_executable(cmdline[0])
      if cmdpath is None:
        raise RuntimeError('{0} command not found; confirm that PATH is properly set'.format(cmdline[0]))
      libpath = os.sep.join(cmdpath.split(os.sep)[:-2] + ['lib'])
      if os.path.isfile(os.sep.join([libpath, 'libjubatus_core.dylib'])):
        # If the estimated libpath is already in the default DYLD_FALLBACK_LIBRARY_PATH,
        # we don't have to add it.  See ``man 1 dyld`` for the list of default search paths.
        if libpath not in [os.path.expanduser('~/lib'), '/usr/local/lib', '/lib', '/usr/lib']:
          envvars['DYLD_FALLBACK_LIBRARY_PATH'] = libpath
          _logger.info('setting DYLD_FALLBACK_LIBRARY_PATH to %s', libpath)
    return subprocess.Popen(cmdline, env=envvars, *args, **kwargs)

class _ServiceBackend(object):
  """
  Service backend handles messy process-related things.
  """

  # Disable verbose tornado WARN logs on connect failure.
  logging.getLogger('tornado').setLevel(logging.ERROR)

  def __init__(self, name, config, port=None):
    self.name = name
    self.config = config
    self.port = port
    self.log = None

    self._logbuf = None
    self._proc = None

    self._check_installed(name)

    (started, log) = self._start()
    if not started:
      raise RuntimeError('failed to start server: {0}'.format(log))

  def __del__(self):
    # Destruct the process.
    try:
      proc = self._proc
      if proc is not None and proc.poll() is None:  # still running
        proc.kill()
        proc.communicate()  # avoid process to become zombie (defunct)
    except Exception as e:
      print('Exception raised while destructing backend process: {0}'.format(e))

    # Destruct the log buffer.
    try:
      logbuf = self._logbuf
      if logbuf is not None and not logbuf.closed:  # log buffer is still open
        logbuf.close()
    except Exception as e:
      print('Exception raised while destructing backend log buffer: {0}'.format(e))

  def _start(self):
    """
    Starts the server instance and returns (is_started, error_log) tuple.
    """
    # Number of retries; if user does not specify port, we can retry.
    retry = 10 if self.port is None else 1

    with tempfile.NamedTemporaryFile(prefix='jubakit-config-') as config_file:
      config_file.write(json.dumps(self.config).encode('utf-8'))
      config_file.flush()

      stdout = None
      for count in range(retry):
        if self.port is None:
          # Randomly pick a port number from TCP ports *currently* free.
          # Note that the port may be in use when jubatus server tries to bind to it.
          self.port = self._get_free_port()

        args = [
          'juba{0}'.format(self.name),
          '--listen_addr', '127.0.0.1',
          '--rpc-port', str(self.port),
          '--timeout', '0',
          '--configpath', config_file.name
        ]

        _logger.debug('trying to start service on port %d: %s', self.port, args)
        self._logbuf = tempfile.NamedTemporaryFile(prefix='jubakit-log-')
        self._proc = JubaProcess.get_process(args, stdout=self._logbuf, stderr=subprocess.STDOUT)
        pid = self._proc.pid

        # Wait until the RPC server start.
        started = self._wait_until_rpc_ready(self.port)

        if started:  # i.e. RPC server is working on the port
          # Get status from the remote server.
          status = None
          try:
            status = self.get_status()
          except Exception as e:
            # Other MessagePack-RPC server that does not respond to get_status RPC (e.g., Jubatus proxy) is running on the port.
            _logger.debug('failed to get status from server on port %d: %s', self.port, str(e))
          if status:
            # Get PID from the server status and compare it with the PID of the process we just started.
            remote_pid = int(status['pid'])
            if remote_pid == pid:
              # Service started successfully.
              _logger.debug('service started on port %d with PID %d', self.port, pid)
              return (True, None)
            # The free port we found was taken by others.
            _logger.debug('service PID mismatch (expected %d, got %d); other Jubatus server is already running on port %d', pid, remote_pid, self.port)
          # Stop the process.
          self._stop()
        else:  # i.e. RPC server is NOT working on the port
          # Stop the process.
          (retval, stdout) = self._stop()

          # Check the log message from the server.
          if 'server failed to start: any process using port' in stdout:
            _logger.debug('service failed to start on port %d; the port is in use', self.port)
          else:
            _logger.debug('service failed to start on port %d: PID %d exit with status %d: %s', self.port, pid, retval, stdout)
            break  # do not retry; seems like it is not a port issue
        self.port = None
      else:  # for count
        _logger.debug('all attempts to start the service failed')  # retry limit reached
    return (False, stdout)

  def _stop(self):
    """
    Stops the server instance and returns (retval, stdout) tuple.
    """
    (proc, logbuf) = (self._proc, self._logbuf)
    (self._proc, self._logbuf) = (None, None)

    if proc is None:
      return (None, None)

    (retval, stdout) = (-1, '(not available)')
    if proc.poll() is None:  # still running
      _logger.debug('process is still running; will be terminated')
      proc.terminate()
    else:
      _logger.debug('process already terminated')
    _logger.debug('waiting for process to exit')
    proc.communicate()
    retval = proc.returncode

    _logger.debug('gathering stdout from server')
    if logbuf is not None and not logbuf.closed:  # log buffer is still open
      logbuf.seek(0)
      stdout = logbuf.read().decode('utf-8')
      logbuf.close()

    return (retval, stdout)

  def stop(self):
    """
    Stops the server instance and return the server log.
    """
    (retval, stdout) = self._stop()
    _logger.debug('process exit with status %d: %s', retval, stdout)
    if retval != 0:
      raise RuntimeError('server exit with status {0}; confirm that the config is valid: {1}'.format(retval, stdout))
    return stdout

  def get_status(self):
    cli = msgpackrpc.Client(msgpackrpc.Address('127.0.0.1', self.port), unpack_encoding='utf-8')
    try:
      return cli.call('get_status', '').popitem()[1]
    finally:
      cli.close()
      cli._loop._ioloop.close()

  @classmethod
  def _get_free_port(cls, start=10000, end=30000):
    """
    Finds the free port available to listen.

    The default range of [10000,30000] is chosen to avoid the default
    ephemeral port range on most platforms.
    """
    used_ports = cls._get_ports_in_use()
    candidates = [x for x in range(start, end + 1) if x not in used_ports]
    if len(candidates) == 0:
      raise RuntimeError('no free port available in range [{0},{1}]'.format(start, end))
    return random.choice(candidates)

  @classmethod
  def _get_ports_in_use(cls):
    """
    Returns a set of ports currently used on localhost.
    """
    try:
      return set([x.laddr[1] for x in psutil.net_connections(kind='inet4')])
    except psutil.AccessDenied:
      # On some platforms (such as OS X), root privilege is required to get used ports.
      # In that case we avoid port confliction to the best of our knowledge.
      _logger.info('ports in use cannot be obtained on this platform; ports will be assigned sequentially')
      return set()

  @classmethod
  def _wait_until_rpc_ready(cls, port):
    sleep_time = 1000
    for i in range(10):
      time.sleep(sleep_time/1000000.0) # from usec to sec
      if cls._ping_rpc(port):
        _logger.debug('service RPC ready after %d tries', i)
        return True
      sleep_time *= 2
    return False

  @classmethod
  def _ping_rpc(cls, port):
    cli = msgpackrpc.Client(msgpackrpc.Address("127.0.0.1", port))
    try:
      cli.call('__ping__')
      raise AssertionError('dummy RPC succeeded')
    except msgpackrpc.error.RPCError as e:
      if e.args[0] == 1:  # "no such method"
        return True
    except:
      return False
    finally:
      cli.close()
      cli._loop._ioloop.close()

    return False

  @classmethod
  def _check_installed(cls, name):
    procname = 'juba{0}'.format(name)

    _logger.debug('checking if service process %s is available', procname)
    try:
      proc = JubaProcess.get_process(
        [procname, '--version'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
      )
      (stdout, _) = proc.communicate()
      if proc.returncode == 0:
        return
      raise RuntimeError('{0} exit with status {1}; confirm that LD_LIBRARY_PATH is properly set: {2}'.format(procname, proc.returncode, stdout))
    except OSError as e:
      raise RuntimeError('{0} could not be started; confirm that PATH is properly set: {1}'.format(procname, e))
