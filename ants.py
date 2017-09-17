from __future__ import division
from __future__ import absolute_import
from random import random

from alg import Algorithm
from edge import Edge
from track import Track
from itertools import ifilter
from itertools import izip


class AntEdge(Edge):
    def __init__(self, edge):
        super(AntEdge, self).__init__(edge.node, edge.length, edge.real)
        edge.pheromone = 1

    @staticmethod
    def reinterpret(edge):
        edge.pheromone = 1
        edge.__class__ = AntEdge

    def __str__(self):
        return unicode(self.pheromone) + u" ~ " + super(AntEdge, self).__str__()


class Ant(object):
    def __init__(self, start, validate=True):
        self.track = Track(start)
        self.validate = validate

    def walk(self, graph):
        n = len(graph.nodes) - 1
        node = self.track.start
        for i in xrange(n):
            edge = self.choose(node)
            self.track.push_edge(edge)
            node = edge.node

        if self.validate:
            self.track.validate(graph)

    def choose(self, node):
        valid_nodes = list(ifilter(lambda edge: edge.node not in self.track.nodes_set, node.edges))

        if len(valid_nodes) == 0:
            raise ValueError(u"Valid nodes exhausted")

        num = random()
        dist = []
        total = 0
        for edge in valid_nodes:
            total += edge.pheromone
            dist.append(total)

        num *= total

        for edge, dist in izip(valid_nodes, dist):
            if num < dist:
                return edge


class ArtificialAnts(Algorithm):
    def __init__(self, function, graph, alpha=0.9, beta=0.1, epsilon=0.1, count=100, iterations=None, seconds=None):
        super(ArtificialAnts, self).__init__(function, iterations, seconds)

        self.graph = graph

        for node in graph.nodes:
            for edge in node.edges:
                AntEdge.reinterpret(edge)

        self.alpha = alpha
        self.beta = beta
        self.epsilon = epsilon
        self.count = count

    def one_step(self):
        ants = list(Ant(self.graph.nodes[i % len(self.graph.nodes)]) for i in xrange(self.count))
        scores = []

        for i, ant in enumerate(ants):
            ant.walk(self.graph)

        for ant in ants:
            score, endpoint = self.evaluate(ant.track)
            #print(str(ant), score)
            scores.append(score)

            for edge in ant.track.edges:
                edge.pheromone += max(score,0)
                # edge.opt_reverse.pheromone += max(score,0)
                #print(edge)
                if edge == endpoint:
                    break

        self.evaporate()
        self.normalize()
        #print(self.graph)
        self.score(scores)

    def normalize(self):
        for node in self.graph.nodes:
            total = sum(edge.pheromone for edge in node.edges)
            for edge in node.edges:
                edge.pheromone /= total

        # for node in self.graph.nodes:
        #     for edge in node.edges:
        #         avg = edge.pheromone + edge.opt_reverse.pheromone
        #         avg *= 0.5
        #         edge.pheromone = avg
        #         edge.opt_reverse.pheromone = avg

    def evaporate(self):
        for node in self.graph.nodes:
            for edge in node.edges:
                edge.pheromone *= self.alpha
                edge.pheromone -= self.beta / len(self.graph.nodes)
                edge.pheromone = max(self.epsilon, edge.pheromone)


