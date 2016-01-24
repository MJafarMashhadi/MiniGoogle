from operator import itemgetter
import random
from math import log2
import json
from clustering.Vector import Vector
from settings import CLUSTER_CANDIDATE_TEXT_LEN, \
    CLUSTER_CANDIDATE_TEXT_DIRECTORY, \
    CLUSTER_SOURCE_DIRECTORY, \
    ELASTIC_URL, INDEX_NAME, DOCUMENT_TYPE, CLUSTER_DESTINATION_DIRECTORY, CLUSTER_NUM
import os
from util import list_files
from elastic.termvector_api import TermVectorAPI

__author__ = 'mohammad hosein'


class K_means:
    centroidList = []
    docCluster = {}
    oldDocCluster = {}
    docVector = {}
    docsJson={}


    def __init__(slef):
        pass

    def initCentroid(self, k):
        self.centroidList = []
        visitedDoc = []
        while len(self.centroidList) < k:
            r = random.randint(0, len(self.docVector))
            if r not in visitedDoc:
                v = Vector()
                v.dict = self.docVector[r].dict.copy()
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
                if t in self.docCluster[c].dict.keys():
                    self.centroidList.dict[t] += self.docVector[d].dict[t]
                else:
                    self.centroidList.dict[t] = self.docVector[d].dict[t]

        for c in range(0, len(self.centroidList)):
            for v in self.centroidList[c].dict.values():
                v /= numberOfDoc[c]


    def terminateCondition(self):
        if len(self.oldDocCluster) == 0:
            return False
        for id in self.docCluster:
            if self.docCluster[id] != self.oldDocCluster[id]:
                return False
        return True


    def findCandidateText(self, k):
        terms = []
        m = [[]] * len(self.centroidList)
        for d in self.docVector.values():
            for t in d.dict.keys():
                if t not in terms:
                    terms.append(t)
                    for c in range(len(self.centroidList)):
                        m[c].append(self.I(t, c))
        result = []
        for d in m:
            result.append(d.sort(reverse=True)[:k])
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
        return n11 / n * log2(n * n11 / (n1_ * n_1)) + n01 / n * log2(n * n01 / (n0_ * n_1)) + n10 / n * log2(
            n * n10 / (n1_ * n_0)) + n00 / n * log2(n * n00 / (n0_ * n_0))

    def clusterDocs(self):
        api = TermVectorAPI(ELASTIC_URL)
        for file in map(lambda x: os.path.join(CLUSTER_SOURCE_DIRECTORY,x),list_files(CLUSTER_SOURCE_DIRECTORY, '*.json')):
            with open(file, 'r') as readFile:
                doc = json.load(readFile)
            self.docsJson[doc['id']]= doc
            self.docVector[doc['id']] = Vector(api.get_term_vector(INDEX_NAME, DOCUMENT_TYPE, doc['id']))

        self.initCentroid(CLUSTER_NUM)

        while True:
            self.oldDocCluster = self.docCluster.copy()
            self.docCluster = {}
            for docID in self.docsJson.keys():
                self.docCluster[docID] = self.nearestCentroid(docID)
            self.updateCentroid()
            if (self.terminateCondition()):
                break

        candids = self.findCandidateText(CLUSTER_CANDIDATE_TEXT_LEN)
        c = [[]] * len(self.centroidList)
        for d in self.docCluster.keys():
            c[self.docCluster[d]].append(d)
        for i in range(len(self.centroidList)):
            res = {}
            res['id'] = i
            res['name'] = candids[i]
            res['pages'] = c[i]
            fileName = i.__str__()+'.json'
            with open(os.path.join(CLUSTER_CANDIDATE_TEXT_DIRECTORY, fileName), 'w') as outfile:
                json.dump(self.URLIDMap, outfile)
        for id in self.docsJson.keys():
            self.docsJson[id]['cluster'] = self.docCluster[id]
            file_name = '{}.json'.format(id)
            with open(os.path.join(CLUSTER_DESTINATION_DIRECTORY , file_name), 'w') as outfile:
                json.dump(self.docsJson[id], outfile)

def main():
    c = K_means()
    c.clusterDocs()
    # url = START_PAGE
    # c.crawl(url, MIN_NUMBER_OF_DOCS)


if __name__ == '__main__':
    main()


