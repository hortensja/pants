from __future__ import division
from __future__ import absolute_import
from track import Track


def offer_value(track):
    pass

def length_inverse(track):
    ret = 1 / track.length()
    return ret, None

def length_inverse_squared(track):
    return 1 / (track.length()**2), None