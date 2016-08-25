# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from jubakit.dumb import Graph
from jubakit._cli.service import GraphCLI

from .base import BaseCLITestCase

class GraphCLITest(BaseCLITestCase):
  def setUp(self):
    self._service = Graph.run(Graph.CONFIG)

  def tearDown(self):
    self._service.stop()

  def test_simple(self):
    self._ok([
      'clear',
      'create_node',            # 0
      'create_node',            # 1
      'create_node',            # 2
      'create_node',            # 3
      'update_node 1 k n1',
      'update_node 2 k n2',
      'update_node 3 k n3',
      'create_edge 1 2 k e4',   # 4
      'create_edge 2 3 k e5',   # 5
      'update_edge 4 1 2 k eX',
      'remove_edge 5',
      'remove_node 3',
      'add_centrality_query',
      'add_shortest_path_query',
      'update_index',
      'get_centrality 1 0',
      'get_shortest_path 1 2',
      'get_shortest_path 1 2 100',
      'remove_centrality_query',
      'remove_shortest_path_query',
      'get_node 1',
      'get_edge 4',
    ])
    self.assertEqual(self._service._client().get_node('1').property, {'k': 'n1'})
    self.assertEqual(self._service._client().get_edge('0', 4).property, {'k': 'eX'})

  def test_fail(self):
    self._fail([
      'create_node foo',
      'update_node',
      'update_node foo bar baz',
      'create_edge foo',
      'update_edge foo bar baz',
      'remove_node foo'
      'remove_edge foo'
      'add_centrality_query foo',
      'add_shortest_path_query foo',
      'update_index foo',
      'get_centrality',
      'get_shortest_path',
      'remove_centrality_query foo',
      'remove_shortest_path_query foo',
      'get_node',
      'get_edge',
    ])
