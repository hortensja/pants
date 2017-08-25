from collections import defaultdict

import pickle

from geocoding import GeoDecoder
from node import Node


THRESHOLD_DISTANCE = 10000
TOLERABLE_DISTANCE = 20

class Graph:
    def __init__(self):
        self.nodes = []
        self.nodes_dict = dict()

    def create_node(self, bb, center, name, coords=None, duplicates=0):
        node = Node(bb, center, name, coords, duplicates)
        self.add_node(node)
        return node

    def add_node(self, node):
        if node.name in self.nodes_dict:
            raise KeyError("Takie miasto juz istnieje")

        self.nodes.append(node)
        self.nodes_dict[node.name] = node

    def get_nodes_by_name(self, name):
        return self.nodes_dict[name]

    def join_node(self, node, decoder):
        for another in self.nodes:
            if another != node:
                distance = decoder.get_naive_distance_from_nodes(node, another).kilometers
                real = False
                if distance > THRESHOLD_DISTANCE:
                    try:
                        distance = decoder.get_driving_distance(node, another)
                        real = True
                    except BaseException as e:
                        print(e)
                        pass
                node.push_sym_edge(another, distance, real)


    def get_path_default(self):
        path = []
        current_node = self.nodes[0]
        while current_node not in path:
            path.append(current_node)
            sorted_edges = sorted(current_node.edges, key=lambda e: e.pheromone, reverse=True)
            for edge in sorted_edges:
                if edge.node not in path:
                    current_node = edge.node
                    break
        return path

    def save(self, where):
        nodes_to_save = list((node.bounding_box, node.records, node.name, node.duplicate) for node in self.nodes)
        edges_to_save = list((node.name, edge.node.name, edge.length, edge.real) for node in self.nodes for edge in node.edges)
        with open(where, "wb") as f:
            pickle.dump((nodes_to_save, edges_to_save), f)

    @staticmethod
    def load(where):
        with open(where, "rb") as f:
            nodes, edges = pickle.load(f)
            ret = Graph()
            for bb, coords, node, duplicate in nodes:
                ret.create_node(bb, None, node, coords, duplicate)

            for edge in edges:
                fro, to, length, real = edge
                fro = ret.get_nodes_by_name(fro)
                to = ret.get_nodes_by_name(to)
                fro.push_sym_edge(to, length, real)

            return ret

    def __str__(self):
        ret = ""
        for node in self.nodes:
            ret += str(node)
        return ret

    def match_duplicates(self, name, gc):
        try:
            alleged_match = self.get_nodes_by_name(name)
            alleged_distance = GeoDecoder.get_naive_distance(gc, alleged_match.center).kilometers
            if alleged_distance < TOLERABLE_DISTANCE:
                print(name, ' already exists in graph: ', alleged_match.short_str())
                alleged_match.duplicate += 1
                raise StopIteration
        except KeyError:
            pass


