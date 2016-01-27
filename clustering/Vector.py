__author__ = 'mohammad hosein'

from math import sqrt

class Vector:
    dict = {}

    def __init__(self, terms=None):
        self.dict = terms if terms else {}

    def size(self):
        return sqrt(sum(map(lambda x: x*x, self.dict.values())))

    def dotp(self, v):
        sum = 0
        for t in self.dict.keys():
            if t in v.dict.keys() :
                sum += self.dict[t] * v.dict[t]
        return sum

    def sim(self, v):
       return 1.0*self.dotp(v)/(self.size()*v.size())

    def distance2(self,V):
        pass
