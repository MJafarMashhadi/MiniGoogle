import os
from settings import PAGERANKALFA, PAGERANKERROR, PAGERANKDESTINATIONDIRECTORY

__author__ = 'mohammad hosein'

import json

import numpy as np
import settings

from util import list_files


class PageRank:
    def __init__(self):
        pass

    def pageRank(self, sourceDirectory, destDirectory):
        docs = []
        id2index = {}
        print('start read files')
        # read files
        for file in map(lambda x: os.path.join(sourceDirectory,x),list_files(sourceDirectory, '*.json')):
            with open(file, 'r') as readFile:
                doc = json.load(readFile)
            id2index[doc['id']] = len(docs)
            docs.append(doc)
        print('statrt calc page rank')
        # create links matrix
        n = len(docs)
        p = []
        for doc in docs:
            pp = [0] * n
            for linkID in filter(lambda x: x in id2index.keys() , (set(doc['cited_in']) |set(doc['refrences'])) ):
                pp[id2index[linkID]] = 1
            p.append(pp)

        # calculate page rank
        pr = self.pageRankMathCalculation(p,PAGERANKALFA,PAGERANKERROR)

        print('start save files')
        # save docs
        os.makedirs(destDirectory, exist_ok=True)
        for doc,pagerank in zip(docs,pr):
            doc['pageRank'] = pagerank
            file_name = '{}.json'.format(doc['id'])
            with open(os.path.join(destDirectory , file_name), 'w') as outfile:
                json.dump(doc, outfile)
        print('end page rank')

    def pageRankMathCalculation(self, p, alfa, error):
        n = len(p)
        sum = np.sum(p, axis=1)
        for i in range(0, n):
            if sum[i] == 0:
                p[i] = np.repeat(1 / n, n)
            else:
                p[i] = np.divide(p[i], sum[i])
        v1 = np.repeat(1 / n, n)
        v = np.tile(v1, [n, 1])

        p = np.add(np.dot(p, (1 - alfa)), np.dot(v, alfa))
        x = np.zeros(n)
        x[0] = 1
        step = 0
        while True:
            step += 1
            pervx = x
            x = np.dot(x, p)
            if (self.calcError(pervx, x) < error):
                break
        print('step = '+ step.__str__())
        return x

    def calcError(self, perv, new):
        sum = 0
        for i in range(0, len(new)):
            sum += abs(new[i] - perv[i])
        return sum



        # a = numpy.zeros(shape=(5,2))
        #
        # >>> np.sum([[0, 1], [0, 5]], axis=1)
        # array([1, 5])
        #
        #
        # from numpy import linalg as LA
        # w, v = LA.eig(a)
        #
        #
        # a = [[1, 0], [0, 1]]
        # >>> b = [[4, 1], [2, 2]]
        # >>> np.dot(a, b)
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        # import numpy as np
        # from scipy.sparse import csc_matrix
        #
        # def pageRank(G, s = .85, maxerr = .001):
        # """
        # Computes the pagerank for each of the n states.
        #     Used in webpage ranking and text summarization using unweighted
        #     or weighted transitions respectively.
        #     Args
        #     ----------
        #     G: matrix representing state transitions
        #        Gij can be a boolean or non negative real number representing the
        #        transition weight from state i to j.
        #     Kwargs
        #     ----------
        #     s: probability of following a transition. 1-s probability of teleporting
        #        to another state. Defaults to 0.85
        #     maxerr: if the sum of pageranks between iterations is bellow this we will
        #             have converged. Defaults to 0.001
        #     """
        #     n = G.shape[0]
        #
        #     # transform G into markov matrix M
        #     M = csc_matrix(G,dtype=np.float)
        #     rsums = np.array(M.sum(1))[:,0]
        #     ri, ci = M.nonzero()
        #     M.data /= rsums[ri]
        #
        #     # bool array of sink states
        #     sink = rsums==0
        #
        #     # Compute pagerank r until we converge
        #     ro, r = np.zeros(n), np.ones(n)
        #     while np.sum(np.abs(r-ro)) > maxerr:
        #         ro = r.copy()
        #         # calculate each pagerank at a time
        #         for i in xrange(0,n):
        #             # inlinks of state i
        #             Ii = np.array(M[:,i].todense())[:,0]
        #             # account for sink states
        #             Si = sink / float(n)
        #             # account for teleportation to state i
        #             Ti = np.ones(n) / float(n)
        #
        #             r[i] = ro.dot( Ii*s + Si*s + Ti*(1-s) )
        #
        #     # return normalized pagerank
        #     return r/sum(r)
        #
        #
        #
        #
        # if __name__=='__main__':
        #     # Example extracted from 'Introduction to Information Retrieval'
        #     G = np.array([[0,0,1,0,0,0,0],
        #                   [0,1,1,0,0,0,0],
        #                   [1,0,1,1,0,0,0],
        #                   [0,0,0,1,1,0,0],
        #                   [0,0,0,0,0,0,1],
        #                   [0,0,0,0,0,1,1],
        #                   [0,0,0,1,1,0,1]])
        #
        #     print pageRank(G,s=.86)


def main():
    print('page rank')
    c = PageRank()
    c.pageRank(settings.PAGERANKRESOURCEDIRECTORY,PAGERANKDESTINATIONDIRECTORY)


if __name__ == '__main__':
    main()