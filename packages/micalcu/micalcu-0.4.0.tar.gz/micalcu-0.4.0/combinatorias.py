from itertools import permutations
from math import factorial

class Combinador:
    def __init__(self, n: int):
        self.n = n

    def total(self):
        return factorial(self.n)

    def iterar(self):
        for p in permutations(range(1, self.n + 1)):
            yield p

