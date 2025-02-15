import json
from math import log2
import os
import random
from operator import itemgetter

from progress.spinner import PieSpinner

from clustering.Vector import Vector
from elastic.termvector_api import TermVectorAPI
from settings import CLUSTER_CANDIDATE_TEXT_LEN, \
    CLUSTER_CANDIDATE_TEXT_DIRECTORY, \
    CLUSTER_SOURCE_DIRECTORY, \
    ELASTIC_URL, INDEX_NAME, DOCUMENT_TYPE, CLUSTER_DESTINATION_DIRECTORY, CLUSTER_NUM
from util import list_files


__author__ = 'mohammad hosein'


class K_means:
    centroidList = []
    docCluster = {}
    oldDocCluster = {}
    docVector = {}
    docsJson={}

    def __init__(self):
        # CLUSTER_NUM = k
        self.progress_bar = PieSpinner('Clustering')

    def initCentroid(self, k):
        self.centroidList = []
        visitedDoc = []
        while len(self.centroidList) < k:
            r = random.choice(list(self.docVector.keys()))
            if r not in visitedDoc:
                visitedDoc.append(r)
                v = Vector(self.docVector[r].dict.copy())
                # v.dict = self.docVector[r].dict.copy()
                self.centroidList.append(v)

    def nearestCentroid(self, docID):
        similarities = [u.sim(self.docVector[docID]) for u in self.centroidList]

        return max(enumerate(similarities), key=itemgetter(1))[0]

    def updateCentroid(self):
        k = len(self.centroidList)
        self.centroidList.clear()
        numberOfDoc = []
        for i in range(0, k):
            self.centroidList.append(Vector())
            numberOfDoc.append(0)

        for d in self.docVector.keys():
            c = self.docCluster[d]
            numberOfDoc[c] += 1
            for t in self.docVector[d].dict.keys():
                if t in self.centroidList[c].dict.keys():
                    self.centroidList[c].dict[t] += self.docVector[d].dict[t]
                else:
                    self.centroidList[c].dict[t] = self.docVector[d].dict[t]

        for c in range(0, len(self.centroidList)):
            for v in self.centroidList[c].dict.values():
                v /= numberOfDoc[c]

    def J(self):
        j = 0
        for d in self.docCluster.keys():
            j += self.docVector[d].distance2(self.centroidList[self.docCluster[d]])
        return j

    def terminateCondition(self):
        if len(self.oldDocCluster) == 0:
            return False
        for id in self.docCluster:
            if self.docCluster[id] != self.oldDocCluster[id]:
                return False
        return True


    def findCandidateText(self, k):
        terms = []
        m = [[] for x in range(len(self.centroidList))]
        for d in self.docVector.values():
            for t in d.dict.keys():
                if t not in terms:
                    terms.append(t)
                    for c in range(len(self.centroidList)):
                        m[c].append(self.I(t, c))
        result = []
        for d in m:
            z = list(zip(d,terms))
            z.sort(key = lambda x:x[0],reverse=True)
            # d.sort(reverse=True)
            result.append(list(map(lambda x: x[1], z[:k])))
        return result


    def I(self, term, cluster):
        n = len(self.docVector)
        n00 = n10 = n11 = n01 = 0

        for id in self.docVector:
            if self.docCluster[id] == cluster:
                if term in self.docVector[id].dict.keys():
                    n11 += 1
                else:
                    n01 += 1
            else:
                if term in self.docVector[id].dict.keys():
                    n10 += 1
                else:
                    n00 += 1
        n1_ = n10 + n11
        n_1 = n01 + n11
        n0_ = n00 + n01
        n_0 = n00 + n10
        # #print('cluster : '+cluster.__str__())
        # #print('n00 = ',n00)
        # #print('n01 = ', n01)
        # #print('n10 = ',n10)
        # #print('n11 = ', n11)
        a1 =  n11 / n * log2(n * n11 / (n1_ * n_1)) if n11 != 0 else 0
        a2 = n01 / n * log2(n * n01 / (n0_ * n_1)) if n01 != 0 else 0
        a3 = n10 / n * log2(n * n10 / (n1_ * n_0)) if n10 != 0 else 0
        a4 = n00 / n * log2(n * n00 / (n0_ * n_0)) if n00 != 0 else 0
        return a1 +a2  + a3 + a4

    def clusterDocs(self):
        api = TermVectorAPI(ELASTIC_URL)
        #print('start read files')
        for file in map(lambda x: os.path.join(CLUSTER_SOURCE_DIRECTORY,x),list_files(CLUSTER_SOURCE_DIRECTORY, '*.json')):
            with open(file, 'r') as readFile:
                doc = json.load(readFile)
            self.docsJson[doc['id']]= doc
            self.docVector[doc['id']] = Vector(api.get_term_vector(INDEX_NAME, DOCUMENT_TYPE, doc['id']))
        #print('read all files successfully')
        #print('start init centroid')
        self.initCentroid(CLUSTER_NUM)
        #print('end init centroid')

        while True:
            self.oldDocCluster = self.docCluster.copy()
            self.docCluster = {}
            for docID in self.docsJson.keys():
                self.docCluster[docID] = self.nearestCentroid(docID)
            self.updateCentroid()
            self.progress_bar.next()
            #print('one step clustring')
            if (self.terminateCondition()):
                self.progress_bar.finish()
                break

        #print('converge clustring')
        print('K = ',CLUSTER_NUM,' J = ',self.J())
        candids = self.findCandidateText(CLUSTER_CANDIDATE_TEXT_LEN)
        #print('calc candid')
        c = [[] for x in range(len(self.centroidList))]
        for d in self.docCluster.keys():
            c[self.docCluster[d]].append(d)
        #print('start save result')
        os.makedirs(CLUSTER_DESTINATION_DIRECTORY, exist_ok=True)
        os.makedirs(CLUSTER_CANDIDATE_TEXT_DIRECTORY, exist_ok=True)
        for i in range(len(self.centroidList)):
            res = {}
            res['id'] = i
            res['name'] = candids[i]
            res['pages'] = c[i]
            fileName = i.__str__()+'.json'
            print('Cluster {}: {}\tnumber of docs: {}', i, ' '.join(candids[i]), len(c[i]))
            #print(res)
            with open(os.path.join(CLUSTER_CANDIDATE_TEXT_DIRECTORY, fileName), 'w') as outfile:
                json.dump(res, outfile)
        for id in self.docsJson.keys():
            self.docsJson[id]['cluster'] = self.docCluster[id]
            file_name = '{}.json'.format(id)
            with open(os.path.join(CLUSTER_DESTINATION_DIRECTORY , file_name), 'w') as outfile:
                json.dump(self.docsJson[id], outfile)
        #print('end save result')

def main():
    c = K_means()
    c.clusterDocs()
    # url = START_PAGE
    # c.crawl(url, MIN_NUMBER_OF_DOCS)


if __name__ == '__main__':
    main()


