# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import threading

try:
  # Python 3
  import queue
except ImportError:
  # Python 2
  import Queue as queue

import tweepy.auth
from tweepy.streaming import StreamListener, Stream
from tweepy.auth import OAuthHandler
import jq

from ..base import BaseLoader
from ..compat import *

class TwitterStreamLoader(BaseLoader):
  """
  Loader to process Twitter Stream.
  Loads statuses only; other type of messages such as direct messages and
  warnings are just ignored.

  ``tweepy`` and ``jq`` package must be installed to use this loader.
  """

  # Keys frequently used are pre-defined.
  # You can optionally specify a list of custom keys (in `jq` selector syntax).
  STATUS_KEYS = [
    # Tweet
    '.id_str',                  # Unique ID
    '.text',                    # Content
    '.lang',                    # Language
    '.favorite_count',          # Num. of favs
    '.retweet_count',           # Num. of RTs
    '.timestamp_ms',            # Timestamp

    # User (the author of the tweet)
    '.user.id',                 # Unique ID
    '.user.name',               # Name
    '.user.screen_name',        # Account (without @ sign)
    '.user.description',        # Profile (bio)
    '.user.lang',               # Language
    '.user.statuses_count',     # Num. of tweets
    '.user.friends_count',      # Num. of followings
    '.user.followers_count',    # Num. of followers
    '.user.favourites_count',   # Num. of favs
    '.user.listed_count',       # Num. of lists author appears
  ]

  # Stream Modes:
  SAMPLE   = 'sample'
  FILTER   = 'filter'
  FIREHOSE = 'firehose'
  USER     = 'user'
  SITE     = 'site'

  def __init__(self, auth=None, mode=SAMPLE, keys=STATUS_KEYS, count=None, **kwargs):
    if auth is None:
      auth = TwitterOAuthHandler()

    self._listener = _TwitterStreamListener(self, keys)
    self._stream = tweepy.streaming.Stream(auth.get(), self._listener, secure=True)
    self._count = count
    self._queue = queue.Queue()

    start_stream = {
      self.SAMPLE:   self._stream.sample,
      self.FILTER:   self._stream.filter,
      self.FIREHOSE: self._stream.firehose,
      self.USER:     self._stream.userstream,
      self.SITE:     self._stream.sitestream,
    }.get(mode, None)

    if start_stream is None:
      raise RuntimeError('unknown stream mode: {0}'.format(mode))

    kwargs['is_async'] = False
    self._thread = threading.Thread(target=start_stream, kwargs=kwargs)
    self._thread.daemon = True

  def is_infinite(self):
    return self._count is None

  def _on_event(self, event):
    self._queue.put(event)

  def rows(self):
    self._thread.start()
    exception = None
    try:
      i = 0
      while True:
        self._listener.check_error()
        try:
          yield self._queue.get(True, 1)
        except queue.Empty:
          continue
        self._queue.task_done()
        i += 1
        if self._count is not None and self._count <= i:
          break
    finally:
      self._stream.disconnect()
      self._thread.join()

class _TwitterStreamListener(tweepy.streaming.StreamListener):
  def __init__(self, loader, keys):
    self._loader = loader
    self._keys = keys
    self._error = None
    super(_TwitterStreamListener, self).__init__()

  def check_error(self):
    if self._error:
      raise self._error

  def on_status(self, status):
    row = dict([(key, jq.jq(key).transform(status._json)) for key in self._keys])
    self._loader._on_event(row)

  def on_error(self, status_code):
    self._error = RuntimeError('Twitter Streaming API returned HTTP error {0}'.format(status_code))

  def on_exception(self, exception):
    self._error = exception

class TwitterOAuthHandler(object):
  """
  Handles authentication required to access Twitter Streaming API.
  """

  def __init__(self, **kwargs):
    """
    Authentication information must be specified as follows:

    >>> TwitterOAuth(
    ...   consumer_key='XXXXXXXXXXXXXXXXXXXX',
    ...   consumer_secret='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    ...   access_token='XXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    ...   access_secret='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    ... )

    If some of keys are not specified, environmenet variables
    (TWITTER_CONSUMER_KEY etc.) will automatically be used.

    You can get your key by registering your app on: https://apps.twitter.com/
    """

    self._kwargs = kwargs

  def _v(self, key):
    if key in self._kwargs:
      return self._kwargs[key]
    envkey = 'TWITTER_{0}'.format(key.upper())
    if envkey in os.environ:
      return os.environ[envkey]
    raise RuntimeError('missing authentication information: {0} must be specified as a constructor argument or environment variable ({1})'.format(key, envkey))

  def get(self):
    auth = tweepy.auth.OAuthHandler(self._v('consumer_key'), self._v('consumer_secret'))
    auth.set_access_token(self._v('access_token'), self._v('access_secret'))
    return auth
