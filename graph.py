from collections import defaultdict

import pickle

from node import Node


class Graph:
    def __init__(self):
        self.nodes = []
        self.nodes_dict = dict()

    def create_node(self, bb, center, name, coords=None):
        node = Node(bb, center, name, coords)
        self.add_node(node)
        return node

    def add_node(self, node):
        if node.name in self.nodes_dict:
            raise KeyError("Takie miasto juz istnieje")

        self.nodes.append(node)
        self.nodes_dict[node.name] = node

    def get_nodes_by_name(self, name):
        return self.nodes_dict[name]

    def save(self, where):
        nodes_to_save = list((node.bounding_box, node.records, node.name) for node in self.nodes)
        edges_to_save = list((node.name, edge.node.name, edge.length) for node in self.nodes for edge in node.edges)
        with open(where, "wb") as f:
            pickle.dump((nodes_to_save, edges_to_save), f)

    @staticmethod
    def load(where):
        with open(where, "rb") as f:
            nodes, edges = pickle.load(f)
            ret = Graph()
            for bb, coords, node in nodes:
                ret.create_node(bb, None, node, coords)

            for edge in edges:
                fro, to, length = edge
                fro = ret.get_nodes_by_name(fro)
                to = ret.get_nodes_by_name(to)
                fro.push_sym_edge(to, length)

            return ret

    def __str__(self):
        ret = ""
        for node in self.nodes:
            ret += str(node)
        return ret

