from track import Track


def length_inverse(track: Track):
    ret = 1 / track.length()
    return ret

def length_inverse_squared(track: Track):
    return 1 / (track.length()**2)