from itertools import imap
class Track(object):
    def __init__(self, start):
        self.edges = []
        self.nodes_set = set()
        self.start = start
        self.nodes_set.add(self.start)

    def push_edge(self, edge):
        self.nodes_set.add(edge.node)
        self.edges.append(edge)

    def validate(self, graph=None):
        if graph is not None:
            if len(self.edges) + 1 != len(graph.nodes):
                raise ValueError(u"Not enough nodes")

            their_set = set(graph.nodes)

            if len(self.nodes_set) != len(self.edges)+1:
                raise ValueError(u"Duplicate edges detected")

            if self.nodes_set != their_set:
                raise ValueError(u"Wrong edges detected")
        else:
            if len(self.nodes_set) != len(self.edges)+1:
                raise ValueError(u"Duplicate edges detected")

    def length(self):
        total = 0
        for edge in self.edges:
            total += edge.length

        return total

    def __str__(self):
        ret = self.start.name
        ret += u" "
        ret += u" ".join(imap(lambda x: x.node.name, self.edges))
        return ret