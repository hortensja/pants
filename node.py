import uuid

from edge import Edge
from geocoding import BoundingBox, GeoCoords





class Node:
    def __init__(self, bb: BoundingBox, center: GeoCoords, name=None, coords=None):
        if name is not None:
            self.name = name
        else:
            self.name = str(uuid.uuid4())
        self.bounding_box = bb
        if coords is not None:
            self.records = coords
        else:
            self.records = [center]
        self.recalc_center()
        self.edges = set()

    def add_record(self, gc: GeoCoords):
        self.records.append(gc)
        self.recalc_center()

    def push_edge(self, other_node, length):
        self.edges.append(Edge(other_node, length, self))

    def push_sym_edge(self, other_node, length):
        one = Edge(other_node, length)
        other = Edge(self, length)

        one.opt_reverse = other
        other.opt_reverse = one

        self.edges.add(one)
        other_node.edges.add(other)

    def recalc_center(self):
        size = len(self.records)
        ret = GeoCoords(0.0, 0.0)
        for coords in self.records:
            ret += coords
        ret.lat /= size
        ret.lng /= size
        self.center = ret
        return ret

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def __str__(self):
        ret = '\n'
        ret += self.name + ' bb: [' + str(self.bounding_box) + '] center: (' + str(self.center) + ') qty: ' + str(len(self.records))
        ret += '\n'
        for edge in self.edges:
            ret += '\t'
            ret += str(edge)
            ret += '\n'
        return ret
