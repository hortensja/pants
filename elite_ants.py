from ants import ArtificialAnts, Ant


class EliteArtificalAnts(ArtificialAnts):
    def __init__(self, function, graph, alpha=0.9, beta=0.1, epsilon=0.1, count=100, iterations=None, seconds=None,
                 normalize=False, city_generator=range):
        ArtificialAnts.__init__(self, function, graph, alpha, beta, epsilon, count, iterations, seconds, normalize,
                                city_generator)

    def one_step(self):
        ants = list(Ant(self.graph.nodes[i % len(self.graph.nodes)]) for i in self.generator(self.count))
        scores = []

        for i, ant in enumerate(ants):
            ant.walk(self.graph)

        max_score = 0
        for ant in ants:
            score, endpoint = self.evaluate(ant.track)
            ant.score = score
            ant.endpoint = endpoint
            max_score = max(score, max_score)
            # print(str(ant), score)
            scores.append(score)

        for ant in ants:
            endpoint = ant.endpoint
            if ant.score == max_score:
                for edge in ant.track.edges:
                    edge.pheromone += max(score, 0)
                    # edge.opt_reverse.pheromone += max(score,0)
                    # print(edge)
                    if edge == endpoint:
                        break

        self.evaporate()
        if self.do_normalize:
            self.normalize()
        # print(self.graph)
        self.score(scores)


