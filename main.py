import json
import random

import pickle

from ants import ArtificialAnts
from csv_reader import get_freight_steps, get_offers, get_freights
from eval_func import length_inverse, length_inverse_squared
from geocoding import BoundingBox, GeoCoords, GeoExtractor, GeoDecoder
from graph import Graph
from neighbors import estimate_offer, OfferEstimate, OfferEvalutaor
from node import Node

from matplotlib import *
from matplotlib.pyplot import *

from prices import PriceInfo, PriceLookup


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
    gdansk = graph.create_node(BoundingBox([0, 1, 2, 3]), GeoCoords(4, 5), "Gdansk")
    gdansk.add_record(GeoCoords(5, 6))
    graph.create_node(BoundingBox([6, 7, 8, 9]), GeoCoords(2, 6), "Braniewo")
    gdansk = graph.get_nodes_by_name("Gdansk")
    braniewo = graph.get_nodes_by_name("Braniewo")
    gdansk.push_sym_edge(braniewo, 100)
    malbork = Node(BoundingBox([4, 3, 2, 1]), GeoCoords(1, 1), "Malbork")
    malbork.push_sym_edge(gdansk, 60)
    braniewo.push_sym_edge(malbork, 60)
    graph.add_node(malbork)
    return graph


def create_real_graph(graph_file="real_shit2", lookup_file=None, base_graph=None, base_lookup=None):
    DECODER_SINGLETON = GeoDecoder()
    # FREIGHT STEPS
    freight_steps = get_freight_steps()
    steps_lookup = base_lookup if base_lookup is not None else {}
    graph = base_graph if base_graph is not None else Graph()
    # node_list = graph.nodes
    node_list = []
    for i, row in enumerate(freight_steps):
        # if i%3 == 0 and i!=0:
        #     graph.save(graph_file)
        #     if lookup_file is not None:
        #         with open(lookup_file, "wb") as f:
        #             pickle.dump(steps_lookup, f)
        #     print('Autosave on iteration: ', i)
        gc = GeoCoords(*row[1:3], reverse=True)
        try:
            match = next(n for n in node_list if n.contains_coords(gc))
            match.add_record(gc)
            name = match.name
            print('Found ', match.short_str(), 'in existing records')
        except StopIteration:
            try:
                geo_json = DECODER_SINGLETON.decode(gc).raw
                name = GeoExtractor.extract_city(geo_json).strip()
                name = graph.match_duplicates(name, gc)
                bb = BoundingBox(GeoExtractor.extract_bounding_box(geo_json))
                node = graph.create_node(bb, gc, name)
                # graph.join_node(node, DECODER_SINGLETON)
                print('Decoded', name, 'successfully')
            except:
                print('Decoding', name, ': ', str(gc), 'failed')
                continue
        step_id = row[0]
        try:
            steps_lookup[step_id].append(name)
        except KeyError:
            steps_lookup[step_id] = [name]
    # print("Finished creating graph from data")
    graph.save(graph_file)
    if lookup_file is not None:
        with open(lookup_file, "wb") as f:
            pickle.dump(steps_lookup, f)
        print('Autosaved location lookup table')
    return graph


def match_freights_make_money(graph, lookup_table_file=None):
    steps = get_freight_steps()
    freights = get_freights()
    if lookup_table_file is None:
        raise NotImplementedError
    f = open(lookup_table_file, 'rb')
    lookup_table = pickle.load(f)
    price_lookup = PriceLookup()
    for freight in freights[1:]:
        freight_id = freight[0]
        freight_steps = []
        for step in steps:
            step_id = step[0]
            if step_id == freight_id:
                freight_steps.append(step)
                # print('Found and saved id, removing')
            elif step_id > freight_id:
                # print("Higher id encountered")
                break
            else:
                # print('Lower id encountered, removing')
                steps.remove(step)
        # print(freight_id, freight_steps, '\n\n')
        # TODO filtering
        if len(freight_steps) > 0:
            try:
                names = lookup_table[freight_id]
                print(names)
                start, end = graph.get_nodes_by_name(names[0]), graph.get_nodes_by_name(names[1])
                price_info = PriceInfo(start, end, *freight[2:5])
                price_lookup.add_price(price_info)
                # for i, freight_step in enumerate(freight_steps):
                #     try:
                #         name = names[i]
                #
                #         print(name, freight)
                #     except IndexError:
                #         print('That should not have happened')
            except KeyError:
                print('Freight id not found in the lookup table')
            except IndexError:
                print('Something is wrong with lookup table', names, 'for freight', freight_id)
    f.close()
    return price_lookup
    # filtered_steps = [s for s in freight_steps if (s[3] == '1' and s[-1] == 'load') or (s[3] == '2' and s[-1] == 'unload')]
    # print(freight_id, filtered_steps, '\n\n')

def prepare_offers(prices, offer_file):
    offers = get_offers()
    estimated_offers = []
    for offer in offers:
        estimated_offers.append(estimate_offer(offer, prices))

    # for offer in estimated_offers:
    #     print(offer)
    with open(offer_file, 'wb') as file:
        pickle.dump(estimated_offers, file)



if __name__ == "__main__":


    # with open("sample_graph200_pheromones.txt", "r") as f:
    #      pheromones = f.read()
    # with open("sample_graph200_legend.txt", "w") as f:
    #     json.dump(", ".join([node.name for node in graph.nodes]), f)
    # print([node.name for node in graph.nodes])
    # print(graph)
    # print('finished reading')
    # offer_list = [OfferEstimate('Gdansk','Braniewo', 0.5, 100), OfferEstimate('Malbork', 'Braniewo', 0.2, 60)] #, OfferEstimate('Braniewo', 'Gdansk', 1.0, 1000)]
    # offer_evaluator = OfferEvalutaor(offer_list)
    # ants = ArtificialAnts(offer_evaluator, graph, alpha=0.6, beta=0.8, epsilon=0.01, iterations=10)
    # ants.run()
    # graph.encode_json('malbork.json')
    # with open(lookup_table, 'rb') as f:
    #     lookup = pickle.load(f)
    # # prices = PriceLookup.load(price_lookup, graph)
    # graph = create_real_graph("real_shit", lookup_table, graph, lookup)
    # graph.save("real_shit")

    # print(graph)
    #
    lookup_table = 'lookup_table.txt'
    price_lookup = 'prices.txt'
    offers = 'estimated_offers.txt'

    graph = Graph.load("dupa")#create_real_graph("dupa", lookup_table)
    # with open(lookup_table, 'rb') as f:
    #     lookup = pickle.load(f)
    # prices = match_freights_make_money(graph, lookup_table)
    #
    prices = PriceLookup.load("new_prices.txt", graph)#.save("new_prices.txt")

    #
    prepare_offers(prices, "offers_experimental.txt")


    # with open(offers, 'rb') as file:
    #     offer_list = pickle.load(file)



    # for offer in offer_list:
    #     print(offer)


    # for p in prices.prices:
    # print(''.join(map(str, prices.prices[p])))



        #
        # offers = get_offers()
        # for offer in offers:
        #     print(offer)

    # graph = create_malbork_graph()
    # offer_list = [OfferEstimate('Gdansk','Braniewo', 0.5, 100), OfferEstimate('Malbork', 'Braniewo', 0.2, 60)] #, OfferEstimate('Braniewo', 'Gdansk', 1.0, 1000)]
    # offer_evaluator = OfferEvalutaor(offer_list)
    # ants = ArtificialAnts(offer_evaluator, graph, alpha=0.6, beta=0.8, epsilon=0.01, iterations=10)
    # ants.run()
    # print(graph)

    # ants.print_score()

    # path = graph.get_path_default()

    # for i, path_node in enumerate(path):
    #     print(i, path_node.name)

    # visited = set()
    # revenue_list = []



    # print('potential revenue:')
    # for revue in revenue_list:
    #     print(revue)

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
