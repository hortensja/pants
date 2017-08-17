import random

from ants import ArtificialAnts
from eval_func import length_inverse, length_inverse_squared
from geocoding import BoundingBox, GeoCoords
from graph import Graph
from node import Node

from matplotlib import *
from matplotlib.pyplot import *

def create_random_graph():
    graph = Graph()
    for i in range(10):
        node = graph.create_node(name=None)
        for another in graph.nodes:
            if node != another:
                node.push_sym_edge(another, random.random())

    return graph


def create_malbork_graph():
    graph = Graph()
    gdansk = graph.create_node(BoundingBox([0,1,2,3]), GeoCoords(4,5), "Gdansk")
    gdansk.add_record(GeoCoords(5,6))
    graph.create_node(BoundingBox([6,7,8,9]), GeoCoords(10,11), "Braniewo")
    gdansk = graph.get_nodes_by_name("Gdansk")
    braniewo = graph.get_nodes_by_name("Braniewo")
    gdansk.push_sym_edge(braniewo, 100)
    malbork = Node(BoundingBox([4,3,2,1]), GeoCoords(12,13), "Malbork")
    malbork.push_sym_edge(gdansk, 60)
    braniewo.push_sym_edge(malbork, 60)
    graph.add_node(malbork)
    return graph

def create_real_graph():
    pass

if __name__ == "__main__":

    #
    # graph = create_random_graph()
    #
    #
    graph = create_malbork_graph()
    graph.save("here")
    graph = Graph.load("here")

    print(graph)

    # ants = ArtificialAnts(length_inverse, graph, alpha=0.95, beta=2, epsilon=0.01, iterations=100)
    #
    # ants.run()
    #
    # print(graph)
    #
    # size = len(ants.max)
    # xs = range(size)
    #
    # plot(xs, ants.max)
    # plot(xs, ants.avg)
    # plot(xs, ants.min)
    #
    # show()

