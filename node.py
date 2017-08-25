import uuid

from edge import Edge
from geocoding import BoundingBox, GeoCoords





class Node:
    def __init__(self, bb: BoundingBox, center: GeoCoords, name=None, coords=None, duplicates=0):
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
        self.duplicate = duplicates

    def add_record(self, gc: GeoCoords):
        self.records.append(gc)
        self.recalc_center()

    def push_edge(self, other_node, length):
        self.edges.append(Edge(other_node, length, self))

    def push_sym_edge(self, other_node, length, real=False):
        one = Edge(other_node, length, real)
        other = Edge(self, length, real)

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

    def contains_coords(self, gc: GeoCoords):
        return gc.is_in_bounding_box(self.bounding_box)

    def short_str(self):
        ret = '\n'
        ret += self.name + ' bb: [' + str(self.bounding_box) + '] center: (' + str(self.center) + ') qty: ' + str(len(self.records) + self.duplicate)
        ret += '\n'
        return ret

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        ret = self.short_str()
        for edge in self.edges:
            ret += '\t'
            ret += str(edge)
            ret += '\n'
        return ret
