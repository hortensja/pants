import csv


def get_freights():
    with open('resources/frachty.csv') as freights:
        freight_reader = csv.reader(freights)
        return list(freight_reader)[1:]


def get_freight_steps():
    with open('resources/kroki_frachtow.csv') as freight_steps:
        step_reader = csv.reader(freight_steps)
        return list(step_reader)[1000:1020]


def get_offers():
    with open('resources/oferty.csv') as offers:
        offer_reader = csv.reader(offers)
        return list(offer_reader)[1:]
