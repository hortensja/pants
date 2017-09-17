from __future__ import with_statement
from __future__ import absolute_import
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
from io import open


def create_random_graph():
    graph = Graph()
    for i in xrange(10):
        node = graph.create_node(name=None)
        for another in graph.nodes:
            if node != another:
                node.push_sym_edge(another, random.random())

    return graph


def create_malbork_graph():
    graph = Graph()
    gdansk = graph.create_node(BoundingBox([0, 1, 2, 3]), GeoCoords(4, 5), u"Gdansk")
    gdansk.add_record(GeoCoords(5, 6))
    graph.create_node(BoundingBox([6, 7, 8, 9]), GeoCoords(10, 11), u"Braniewo")
    gdansk = graph.get_nodes_by_name(u"Gdansk")
    braniewo = graph.get_nodes_by_name(u"Braniewo")
    gdansk.push_sym_edge(braniewo, 100)
    malbork = Node(BoundingBox([4, 3, 2, 1]), GeoCoords(12, 13), u"Malbork")
    malbork.push_sym_edge(gdansk, 60)
    braniewo.push_sym_edge(malbork, 60)
    graph.add_node(malbork)
    return graph


def create_real_graph(lookup_file=None):
    DECODER_SINGLETON = GeoDecoder()
    lat, lng = [], []
    # FREIGHT STEPS
    freight_steps = get_freight_steps()
    node_list = []
    steps_lookup = {}
    graph = Graph()
    for row in freight_steps:
        gc = GeoCoords(*row[1:3], reverse=True)
        lat.append(gc.lat)
        lng.append(gc.lng)
        name = u'dupa'
        try:
            match = [n for n in node_list if n.contains_coords(gc).next()]
            match.add_record(gc)
            name = match.name
            print u'Found ', match.short_str(), u'in existing records'
        except StopIteration:
            try:
                geo_json = DECODER_SINGLETON.decode(gc).raw
                name = GeoExtractor.extract_city(geo_json).strip()
                graph.match_duplicates(name, gc)
                bb = BoundingBox(GeoExtractor.extract_bounding_box(geo_json))
                node = graph.create_node(bb, gc, name)
                graph.join_node(node, DECODER_SINGLETON)
                node_list.append(node)
                print u'Decoded', name, u'successfully'
            except:
                print u'Decoding', name, u': ', unicode(gc), u'failed'
                continue
        step_id = row[0]
        try:
            steps_lookup[step_id].append(name)
        except KeyError:
            steps_lookup[step_id] = [name]
    print u"Finished creating graph from data"
    if lookup_file is not None:
        with open(lookup_file, u"wb") as f:
            pickle.dump(steps_lookup, f)
        print u'Saved location lookup table'
    return graph


def match_freights_make_money(graph, lookup_table_file=None):
    steps = get_freight_steps()
    freights = get_freights()
    if lookup_table_file is None:
        raise NotImplementedError
    f = open(lookup_table_file, u'rb')
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
                print names
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
                print u'Freight id not found in the lookup table'
            except IndexError:
                print u'Something is wrong with lookup table', names, u'for freight', freight_id
    return price_lookup
    # filtered_steps = [s for s in freight_steps if (s[3] == '1' and s[-1] == 'load') or (s[3] == '2' and s[-1] == 'unload')]
    # print(freight_id, filtered_steps, '\n\n')

def prepare_offers(prices, offer_file):
    offers = get_offers()
    estimated_offers = []
    for offer in offers[1:]:
        estimated_offers.append(estimate_offer(offer, prices))

    for offer in estimated_offers:
        print offer
    with open(offer_file, u'wb') as file:
        pickle.dump(estimated_offers, file)



if __name__ == u"__main__":
    lookup_table = u'lookup_table.txt'
    price_lookup = u'prices.txt'
    offers = u'estimated_offers.txt'

    # graph = create_real_graph(lookup_table)
    # graph.save("here")
    graph = Graph.load(u"here")

    # print(graph)
    #
    # prices = match_freights_make_money(graph, lookup_table)
    #
    # prices.save(price_lookup)

    # prices = PriceLookup.load(price_lookup, graph)
    #
    # prepare_offers(prices, offers)


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

    graph = create_malbork_graph()

    offer_list = [OfferEstimate(u'Gdansk',u'Braniewo', 0.5, 100), OfferEstimate(u'Malbork', u'Braniewo', 0.2, 60)] #, OfferEstimate('Braniewo', 'Gdansk', 1.0, 1000)]

    offer_evaluator = OfferEvalutaor(offer_list)

    ants = ArtificialAnts(offer_evaluator, graph, alpha=0.6, beta=0.8, epsilon=0.01, iterations=10)

    ants.run()
    # print(graph)

    # ants.print_score()

    path = graph.get_path_default()

    # for i, path_node in enumerate(path):
    #     print(i, path_node.name)

    visited = set()
    revenue_list = []



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
