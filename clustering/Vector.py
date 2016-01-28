__author__ = 'mohammad hosein'

from math import sqrt

class Vector:
    dict = {}

    def __init__(self, terms=None):
        self.dict = terms if terms else {}

    def size(self):
        return sqrt(sum(map(lambda x: x*x, self.dict.values())))

    def dotp(self, v):
        return sum((self.dict[t] * v.dict[t] for t in self.dict.keys() & v.dict.keys()))

    def sim(self, v):
       return 1.0*self.dotp(v)/(self.size()*v.size())

    def distance2(self,v):
        res = 0
        for t in self.dict.keys():
            if t in v.dict.keys():
                res += (self.dict[t]-v.dict[t])**2
            else:
                res += self.dict[t]**2

        for t in v.dict.keys():
            if t not in self.dict.keys():
                res += v.dict[t]**2
        return res

