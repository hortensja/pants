from track import Track


def offer_value(track: Track):
    pass

def length_inverse(track: Track):
    ret = 1 / track.length()
    return ret, None

def length_inverse_squared(track: Track):
    return 1 / (track.length()**2), None