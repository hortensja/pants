class Edge(object):
    def __init__(self, node, length, opt_reverse=None, real=False):
        self.node = node
        self.length = length
        self.opt_reverse = opt_reverse
        self.real = real

    def __str__(self):
        ret = u"--- "
        ret += unicode(round(self.length, 2))
        ret += u' (real) ' if self.real else u''  # ' (appr) '
        ret += u" ---> "
        ret += self.node.name
        return ret

    def __hash__(self):
        return hash(self.node.name)

    def __eq__(self, other):
        return self.node.name == other.node.name
