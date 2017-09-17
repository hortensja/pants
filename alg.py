from __future__ import absolute_import
import time

from track import Track


class Algorithm(object):
    def __init__(self, function, iterations=None, seconds=None):
        self.evaluation_function = function

        if iterations is None and seconds is None:
            iterations = 1

        self.iterations = iterations

        self.it = 0

        self.seconds = seconds

        self.start = None

        self.avg = []
        self.max = []
        self.min = []

    def one_step(self):
        pass

    def run(self):
        self.start = time.time()
        while True:
            self.one_step()

            self.it += 1

            if self.seconds is not None:
                now = time.time()
                if now - self.start > self.seconds:
                    break

            if self.iterations is not None:
                if self.it >= self.iterations:
                    break

    def evaluate(self, track):
        return self.evaluation_function(track)

    def score(self, scores):
        avg = 0
        best = float(u'inf')
        worst = -float(u'inf')

        for score in scores:
            avg += score
            best = min(score, best)
            worst = max(score, worst)

        avg /= len(scores)

        self.avg.append(avg)
        self.max.append(best)
        self.min.append(worst)

    def print_score(self):
        print u'avg:', self.avg, u'min:',self.min, u'max:',self.max
