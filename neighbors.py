from __future__ import absolute_import
import numpy as np
import pylab as plt

from geocoding import GeoDecoder, GeoCoords
from track import Track
from itertools import imap

NUMBER_OF_NEIGHBORS = 5


def wtf_function(x, y):
    return np.sin(x * y) ** 2 + np.cos(x ** 2 + y ** 2)


def base_distance(gc1, gc2):
    return GeoDecoder.get_naive_distance(gc1, gc2).kilometers


def estimate_offer(offer, price_lookup):
    offer_gc = offer[3:7]
    offer_start_gc = GeoCoords(offer[3], offer[4])
    offer_end_gc = GeoCoords(offer[5], offer[6])
    price_info_list = [price_info[1] for price_info in price_lookup.prices.items()]
    sorted_lookup = sorted(price_info_list, key=lambda price: base_distance(offer_start_gc, price[0].start.center) + base_distance(offer_end_gc, price[0].end.center))
    best_neighbors = [neighbor[0].calculate_price()[0] for neighbor in sorted_lookup][:NUMBER_OF_NEIGHBORS]

    mean = np.mean(best_neighbors)

    geoDecoder = GeoDecoder()
    start = geoDecoder.get_city_default(offer_start_gc)
    end = geoDecoder.get_city_default(offer_end_gc)
    return OfferEstimate(start, end, mean, base_distance(offer_start_gc, offer_end_gc))


def gupia_function(truX, truY, X, Y):
    #print(X.shape)
    dupa = np.multiply.reduce(X.shape)
    X = X.reshape(dupa)
    Y = Y.reshape(np.multiply.reduce(Y.shape))
    truX = truX.reshape(np.multiply.reduce(truX.shape))
    truY = truY.reshape(np.multiply.reduce(truY.shape))
    trutruXY = np.array((truX, truY)).T
    eror_table = []
    for i in xrange(dupa):
        x, y = X[i], Y[i]
        xy = (x, y)
        trutruXY = sorted(trutruXY, key=lambda p: dystance(xy, p))
        neighbors = np.array(trutruXY[:NUMBER_OF_NEIGHBORS]).T
        meaningless = np.mean(wtf_function(*neighbors))
        eror = abs(meaningless - wtf_function(x, y))
        eror_table.append(eror)
        # return 69
    print np.mean(eror_table)
    return np.array(eror_table).reshape((10, 10))


class OfferEstimate(object):
    def __init__(self, start, end, price_per_km, length=None):
        self.start = start
        self.end = end
        self.price_per_km = float(price_per_km)
        self.length = float(length)
        self.total = None
        self.calculate()

    def calculate(self):
        if self.length is None:
            # TODO smart way to find length
            self.length = 69
        self.total = self.price_per_km * self.length

    def __str__(self):
        ret = u'Offer '
        ret += self.start
        ret += u'-'
        ret += self.end
        ret += u': '
        ret += unicode(round(self.price_per_km, 2))
        ret += u'*'
        ret += unicode(round(self.length,1))
        ret += u'='
        ret += unicode(round(self.total, 2))
        return ret

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.start == other.start and self.end == other.end and \
               self.length == other.length and self.price_per_km == other.price_per_km

    def __hash__(self):
        return hash(self.start) + hash(self.end)

if __name__ == u"__main__":
    #print("kupa")

    # Sample data
    side = np.linspace(-2, 2, 10)
    X, Y = np.meshgrid(side, side)

    truX, truY = np.random.rand(2, 10, 10) * 4 - 2

    Z = gupia_function(truX, truY, X, Y)
    # # print(X,Y)
    # Z = fajna_function(X, Y)
    # # print(Z)
    # # Plot the density map using nearest-neighbor interpolation
    #
    fig = plt.figure(facecolor=u'k')
    ax = fig.add_subplot(111, projection=u'3d')

    ax.plot_wireframe(X=X, Y=Y, Z=Z)
    plt.show()

class OfferEvalutaor(object):
    def __init__(self, offer_list):
        self.offer_list = offer_list

    @staticmethod
    def calculate_revenue(chosen_ones):
        return sum(imap(lambda x: x.total, chosen_ones))

    def __call__(self, track):
        revenue_list = []
        visited = set()
        visited.add(track.start.name)
        offer_list = list(self.offer_list)
        for i, edge in track.edges:
            city = edge.node
            visited.add(city.name)
            to_remove = []
            chosen_ones = set()
            chosen_list = []
            for offer in offer_list:
                if offer.start in visited and offer.end == city.name:
                    chosen_ones.add(offer)
                    chosen_list.append(offer)
                if offer.end in visited:
                    to_remove.append(offer)
            for bad_offer in to_remove:
                offer_list.remove(bad_offer)
            # for chosen_one in chosen_ones:
                # print(chosen_one)
            revenue_list.append((OfferEvalutaor.calculate_revenue(chosen_ones) - edge.length*0.4 + (revenue_list[-1][0] if len(revenue_list) > 0 else 0), edge))
        #print(max(revenue_list, key=lambda x: x[0])[0], str(track))
        best = max(revenue_list, key=lambda x: x[0])
        return best, chosen_list[0:chosen_list.index(best[1])+1]
