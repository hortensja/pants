from __future__ import with_statement
from __future__ import absolute_import
import csv
from io import open


def get_freights():
    with open(u'resources/freights_test.csv') as freights:
        freight_reader = csv.reader(freights)
        return list(freight_reader)


def get_freight_steps():
    with open(u'resources/freight_steps_test.csv') as freight_steps:
        step_reader = csv.reader(freight_steps)
        return list(step_reader)


def get_offers():
    with open(u'resources/offers_test.csv') as offers:
        offer_reader = csv.reader(offers)
        return list(offer_reader)
