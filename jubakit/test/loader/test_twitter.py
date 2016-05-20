# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.loader.twitter import TwitterStreamLoader, TwitterOAuthHandler

class TwitterStreamLoaderTest(TestCase):
  oauth = TwitterOAuthHandler(consumer_key='x', consumer_secret='x', access_token='x', access_secret='x')

  def test_simple(self):
    loader = TwitterStreamLoader(self.oauth)

  def test_errors(self):
    # auth info (both os.environ and auth argument) is not set
    self.assertRaises(RuntimeError, TwitterStreamLoader)

    # invalid stream name
    self.assertRaises(RuntimeError, TwitterStreamLoader, self.oauth, 'invalid_mode')
