# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from jubatus.graph.types import *

from .generic import GenericCLI
from ..args import Arguments, Optional, TProperty
from ..util import *
from ..._stdio import print

class GraphCLI(GenericCLI):
  @classmethod
  def _name(cls):
    return 'graph'

  @Arguments()
  def do_create_node(self):
    """Syntax: create_node
    Create node.
    """
    result = self.client.create_node()
    print(result)

  @Arguments(str)
  def do_remove_node(self, node_id):
    """Syntax: remove_node node_id
    Remove the specified node.
    """
    result = self.client.remove_node(node_id)
    if not result:
      print("Failed")

  @Arguments(str, TProperty)
  def do_update_node(self, node_id, prop):
    """Syntax: update_node node_id [property_key property_value ...]
    Update node.
    """
    result = self.client.update_node(node_id, prop)
    if not result:
      print("Failed")

  @Arguments(str, str, Optional(TProperty))
  def do_create_edge(self, from_node_id, to_node_id, prop):
    """Syntax: create_edge from_node to_node [property_key property_value ...]
    Create edge.
    """
    if prop is None:
      prop = {}
    info = Edge(prop, from_node_id, to_node_id)
    result = self.client.create_edge(from_node_id, info)
    print("Edge ID: {0}".format(result))

  @Arguments(int, str, str, Optional(TProperty))
  def do_update_edge(self, edge_id, from_node_id, to_node_id, prop):
    """Syntax: update_edge edge_id from_node to_node [property_key property_value ...]
    Update edge.
    """
    if prop is None:
      prop = {}
    info = Edge(prop, from_node_id, to_node_id)
    result = self.client.update_edge(from_node_id, edge_id, info)
    if not result:
      print("Failed")

  @Arguments(int, Optional(str))
  def do_remove_edge(self, edge_id, from_node_id):
    """Syntax: remove_edge edge_id [from_node]
    Remove the specified edge.
    from_node is mandatory when in distributed mode.
    """
    if from_node_id is None:
      from_node_id = ""
    result = self.client.remove_edge(from_node_id, edge_id)
    if not result:
      print("Failed")

  @Arguments(str, Optional(int))
  def do_get_centrality(self, node_id, c_type):
    """Syntax: get_centrality node_id [type]
    Calculate centrality for the node.
    "type" is 0 (PageRank) by default.
    Currenetly, only empty query is supported.
    """
    if c_type is None:
      c_type = 0
    query = PresetQuery([], [])
    centrality = self.client.get_centrality(node_id, c_type, query)
    print(centrality)

  @Arguments()
  def do_add_centrality_query(self):
    """Syntax: add_centrality_query
    Preset centrality query.
    Currenetly, only empty query is supported.
    """
    query = PresetQuery([], [])
    result = self.client.add_centrality_query(query)
    if not result:
      print("Failed")

  @Arguments()
  def do_add_shortest_path_query(self):
    """Syntax: add_shortest_path_query
    Preset shortest_path query.
    Currenetly, only empty query is supported.
    """
    query = PresetQuery([], [])
    result = self.client.add_shortest_path_query(query)
    if not result:
      print("Failed")

  @Arguments()
  def do_remove_centrality_query(self):
    """Syntax: remove_centrality_query
    Remove preset centrality query.
    Currenetly, only empty query is supported.
    """
    query = PresetQuery([], [])
    result = self.client.remove_centrality_query(query)
    if not result:
      print("Failed")

  @Arguments()
  def do_remove_shortest_path_query(self):
    """Syntax: remove_shortest_path_query
    Remove preset shortest_path query.
    Currenetly, only empty query is supported.
    """
    query = PresetQuery([], [])
    result = self.client.remove_shortest_path_query(query)
    if not result:
      print("Failed")

  @Arguments(str, str, Optional(int))
  def do_get_shortest_path(self, src_node, dst_node, max_hop):
    """Syntax: get_shortest_path src_node dst_node [max_hop]
    Calculates the shortest path from src_node to dst_node.
    """
    if max_hop is None:
      max_hop = pow(2, 32) - 1
    query = PresetQuery([], [])
    req = ShortestPathQuery(src_node, dst_node, max_hop, query)
    nodes = self.client.get_shortest_path(req)
    for node in nodes:
      print(node)

  @Arguments()
  def do_update_index(self):
    """Syntax: update_index
    Updates the index.
    You cannot use this method in distributed configuration.
    """
    result = self.client.update_index()
    if not result:
      print("Failed")

  @Arguments(str)
  def do_get_node(self, node_id):
    """Syntax: get_node node_id
    Get node information.
    """
    info = self.client.get_node(node_id)
    print("Properties:")
    for key in info.property:
      print("  {0}: {1}".format(key, info.property[key]))
    print("In-Edges:")
    print("  {0}".format(str(info.in_edges)))
    print("Out-Edges:")
    print("  {0}".format(str(info.out_edges)))

  @Arguments(int, Optional(str))
  def do_get_edge(self, edge_id, from_node_id):
    """Syntax: get_edge edge_id [from_node_id]
    Get edge information.
    from_node_id is mandatory when in distributed mode.
    """
    if from_node_id is None:
      from_node_id = "0"
    info = self.client.get_edge(from_node_id, edge_id)
    print("Properties:")
    for key in info.property:
      print("  {0}: {1}".format(key, info.property[key]))
    print("Source     : {0}".format(info.source))
    print("Destination: {0}".format(info.target))
