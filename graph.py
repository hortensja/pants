from __future__ import with_statement
from __future__ import absolute_import
import json
import pickle

from geocoding import GeoDecoder
from node import Node
from io import open


THRESHOLD_DISTANCE = 250
TOLERABLE_DISTANCE = 15

class Graph(object):
    def __init__(self):
        self.nodes = []
        self.nodes_dict = dict()
        self.hard_cases = dict()

    def create_node(self, bb, center, name, coords=None, duplicates=0):
        node = Node(bb, center, name, coords, duplicates)
        self.add_node(node)
        return node

    def add_node(self, node):
        if node.name in self.nodes_dict:
            raise KeyError(u"City "+node.name+u" already exists in graph")

        self.nodes.append(node)
        self.nodes_dict[node.name] = node

    def get_nodes_by_name(self, name):
        return self.nodes_dict[name]

    def join_node(self, node, decoder):
        for another in self.nodes:
            if another != node:
                distance = decoder.get_naive_distance_from_nodes(node, another)
                real = False
                if distance > THRESHOLD_DISTANCE:
                    try:
                        distance = decoder.get_driving_distance(node, another)
                        real = True
                    except BaseException, e:
                        print e
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
        with open(where, u"wb") as f:
            pickle.dump((nodes_to_save, edges_to_save), f)

    @staticmethod
    def load(where):
        with open(where, u"rb") as f:
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
        ret = u""
        for node in self.nodes:
            ret += unicode(node)
        return ret

    def encode_json(self, filename=u'dupa.json'):
        json_obj = {}
        nodes_list = []
        edges_list = []
        for node in self.nodes:
            print u'processing ', node.name
            node_json = {u'id': node.name, u'label': node.name, u'size': node.duplicate+1,u'x': node.center.lng, u'y': node.center.lat}
            nodes_list.append(node_json)
            for i,edge in enumerate(node.edges):
                edge_json = {u'id': node.name + unicode(i), u'source': node.name, u'target': edge.node.name, u'size': edge.pheromone*10}
                edges_list.append(edge_json)
        json_obj[u'nodes'] = nodes_list
        json_obj[u'edges'] = edges_list
        with open(filename, u'w') as f:
            json.dump(json_obj, f)
        return json_obj

    def arraify(self):
        ret = []
        for node in self.nodes:
            row = []
            for also_node in self.nodes:
                edge = node.get_edge_by_target(also_node)
                val = edge.length if edge is not None else 0
                row.append(val)
            ret.append(row)
        return ret

    def dearraify(self, pheromones):
        for i, row in enumerate(pheromones):
            for j, phe in enumerate(row):
                target = self.nodes[j]
                edge = self.nodes[i].get_edge_by_target(target)
                if edge is not None:
                    edge.pheromone = phe


    def match_duplicates(self, name, gc):
        try:
            alleged_match = self.get_nodes_by_name(name)
            alleged_distance = GeoDecoder.get_naive_distance(gc, alleged_match.center).kilometers
            if alleged_distance < TOLERABLE_DISTANCE:
                print name, u' already exists in graph: ', alleged_match.short_str()
                alleged_match.duplicate += 1
                raise StopIteration
            else:
                try:
                    self.hard_cases[name]
                except KeyError:
                    self.hard_cases[name] = []
                cases = self.hard_cases[name]
                name += unicode(len(cases))
                self.hard_cases[name].append(name)
                return name
        except KeyError:
            return name


