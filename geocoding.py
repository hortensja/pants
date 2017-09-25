from datetime import datetime

# import googlemaps
import googlemaps
from geopy import geocoders as ggc, distance as gdst


def floatize(x):
    return list(map(float, x))


class BoundingBox:
    def __init__(self, coords, reverse=False):
        lats = coords[0:2]
        lngs = coords[2:4]
        if reverse:
            lats, lngs = lngs, lats

        self.lats = floatize(lats)
        self.lngs = floatize(lngs)

    def __str__(self):
        return "lat: " + str(self.lats) + ", lng: " + str(self.lngs)


class GeoCoords:
    def __init__(self, lat, lng, reverse=False):
        if reverse:
            lat, lng = lng, lat
        self.lat = float(lat)
        self.lng = float(lng)

    def is_in_bounding_box(self, bb: BoundingBox):
        lat_bounds = bb.lats
        if self.lat < lat_bounds[0] or self.lat > lat_bounds[1]:
            return False
        lng_bounds = bb.lngs
        if self.lng < lng_bounds[0] or self.lng > lng_bounds[1]:
            return False
        return True

    def __add__(self, other):
        return GeoCoords(self.lat + other.lat, self.lng + other.lng)

    def __str__(self):
        return str(self.lat) + "," + str(self.lng)


class GeoDecoder:
    def __init__(self):
        self.geolocator = ggc.Nominatim()
        self.gmaps = googlemaps.Client(key='AIzaSyCZMpHt9d-_f0LntNKZ76CwCnuuPbQiCqI')

    def decode(self, coords: GeoCoords):
        location = self.geolocator.reverse(str(coords))
        return location

    def get_driving_distance(self, city1, city2):
        try:
            response = self.gmaps.distance_matrix(origins=city1.name, destinations=city2.name,
                                     mode="driving")
            value = response['rows'][0]['elements'][0]['distance']['value']
            print('google OK')
            return float(value) / 1000
        except:
            print('google y u no work')
            return GeoDecoder.get_naive_distance_from_nodes(city1, city2)

    def get_city_default(self, gc: GeoCoords):
        geo_json = self.decode(gc).raw
        return GeoExtractor.extract_city(geo_json).strip()

    @staticmethod
    def get_naive_distance_from_nodes(city1, city2):
        return GeoDecoder.get_naive_distance(city1.center, city2.center).kilometers

    @staticmethod
    def get_naive_distance(gc1, gc2):
        try:
            return gdst.distance(str(gc1), str(gc2))
        except:
            return KeyError


class GeoExtractor:
    @staticmethod
    def extract_city(geo_json):
        try:
            address = geo_json['address']
        except KeyError:
            return None
        try:
            return address['city']
        except KeyError:
            try:
                return address['town']
            except KeyError:
                try:
                    return address['village']
                except KeyError:
                    # return None
                    return address

    @staticmethod
    def extract_bounding_box(geo_json):
        try:
            return geo_json['boundingbox']
        except KeyError:
            return None

    @staticmethod
    def extract_distance_and_time(dist_json):
        try:
            data = dist_json['rows']['elements']
            return (data['distance'], data['duration'])
        except KeyError:
            return None




            # if __name__ == '__main__':
            #     geod = GeoDecoder()
            #     gc = GeoCoords(52.509669, 13.376294)
            #     print(geod.decode(gc).raw)


            # location = geolocator.reverse("52.509669, 13.376294")
            # print(location.address)
            # print(location.raw)


            # Geocoding an address
            # geocode_result = gmaps.geocode('chylonska 65, gdynia')

            # print(geocode_result)

            # Look up an address with reverse geocoding
            # reverse_geocode_result = gmaps.reverse_geocode((49.1781000, 9.5050000))

            # print(reverse_geocode_result)
