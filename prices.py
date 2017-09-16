from __future__ import *
import pickle


class PriceInfo:
    def __init__(self, start, end, empty_dist=0, loaded_dist=0, price=0, length=0):
        self.start = start
        self.end = end
        self.empty_dist = float(empty_dist)
        self.loaded_dist = float(loaded_dist)
        self.price = float(price)

    def calculate_price(self):
        per_all = self.price / (self.empty_dist + self.loaded_dist)
        per_load = self.price / self.loaded_dist

        return per_load, per_all

    def __str__(self):
        ret = '|'
        ret += str(self.start)
        ret += ' -> '
        ret += str(self.end)
        prices = self.calculate_price()
        ret += '| load: '
        ret += str(prices[0])
        ret += '\t'
        return ret


class PriceLookup:
    def __init__(self):
        self.prices = {}

    def add_price(self, price_info):
        start = price_info.start
        try:
            self.prices[start].append(price_info)
        except KeyError:
            self.prices[start] = [price_info]

    def save(self, where):
        prices = {}
        for key, price in self.prices.items():
            fees = []
            for fee in price:
                fees.append((fee.start.name, fee.end.name, fee.empty_dist, fee.loaded_dist, fee.price))
            prices[key.name] = fees
        with open(where, "wb") as f:
            pickle.dump(prices, f)

    @staticmethod
    def load(where, graph):
        with open(where, "rb") as f:
            prices = pickle.load(f)
            price_lookup = PriceLookup()
            for key, price in prices.items():
                start = graph.get_nodes_by_name(key)
                for fee in price:
                    end = graph.get_nodes_by_name(fee[1])
                    price_info = PriceInfo(start, end, *fee[2:])
                    price_lookup.add_price(price_info)
            return price_lookup
