from __future__ import with_statement
from __future__ import absolute_import
import csv
from io import open


def get_freights():
    with open(u'resources/frachty.csv') as freights:
        freight_reader = csv.reader(freights)
        return list(freight_reader)[1:]


def get_freight_steps():
    with open(u'resources/kroki_frachtow.csv') as freight_steps:
        step_reader = csv.reader(freight_steps)
        return list(step_reader)[1000:1020]


def get_offers():
    with open(u'resources/oferty.csv') as offers:
        offer_reader = csv.reader(offers)
        return list(offer_reader)[1:]
