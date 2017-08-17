class Edge:
    def __init__(self, node, length, opt_reverse = None):
        self.node = node
        self.length = length
        self.opt_reverse = opt_reverse

    def __str__(self):
        ret = "--- "
        ret += str(self.length)
        ret += " ---> "
        ret += self.node.name
        return ret

    def __hash__(self):
        return hash(self.node.name)

    def __eq__(self, other):
        return self.node.name == other.node.name
