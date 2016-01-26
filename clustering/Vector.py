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

    # def vec_sum(self ,vec_list):
    #    vsum = [0 for x in range(len(vec_list[0]))]
    #    for vec in vec_list:
    #       vsum = [s+x for s,x in zip(vsum, vec)]
    #    return vsum
    #
    # def vec_average(self,vec_list):
    #    return list(map(lambda x: x/len(vec_list), vec_sum(vec_list)))
    #
    # def belongs_to_cluster(self , v, centeroids):
    #    similarities = [sim(u, v) for u in centeroids]
    #    print ('similarities for', v, '=', similarities)
    #    return max(enumerate(similarities), key=itemgetter(1))[0]
