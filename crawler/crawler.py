import threading

__author__ = 'mohammad hosein'

import json
import threading

import os
import re
import requests
from bs4 import BeautifulSoup
from settings import NUMBER_OF_THREADS, START_PAGE, MIN_NUMBER_OF_DOCS, \
    MAP_FILE_NAME, ERRORS_FILE_NAME, AFTER_CRAWL_BASE_DIR
from .crawl_thread import CrawlThread


class Crawler:
    def __init__(self):
        self.URLIDMap = {}
        self.visitedURLs = set()
        self.visitedTitles = set()
        self.numberOfVisitedPage = 0
        self.queue = list()
        self.lockQueue = threading.Lock()
        self.lockAdd = threading.Lock()
        self.baseURL = 'https://www.researchgate.net/'

    def parseArticlePage(self, url):
        id = self.getIDFromURL(url)

        r = requests.get(url)
        s = BeautifulSoup(r.text, 'html.parser')
        title = s.find('h1', class_='pub-title')
        title = title.text
        authors = s.findAll('a', class_='display-name')
        authorsList = []
        for author in authors:
            authorsList += [author.text]
        abstract = s.find('div', class_='pub-abstract').div.div.text

        headers = {
            'accept': 'application/json',
            'x-requested-with': 'XMLHttpRequest',
        }

        js_url_citedin = 'https://www.researchgate.net/publicliterature.PublicationIncomingCitationsList.html?publicationUid=' + id + '&useUpdatedLayoutForPublicationItems=false&loadAuthorImageLinks=false&getCommentCount=false&usePlainButton=false&useEnrichedContext=false&showAbstract=false&showType=false&showDownloadButton=false&showOpenReviewButton=false&showPublicationPreview=false&swapJournalAndAuthorPositions=false&showContexts=false&limit=10&loadMoreCount=1'
        r2 = requests.get(js_url_citedin, headers=headers)
        jsonObject = json.loads(r2.text)
        citedinURLs = []
        citedinIDs = []
        for citation in jsonObject['result']['data']['citationItems']:
            citedinURLs.append(self.baseURL + citation['data']['url'])
            citedinIDs.append(citation['data']['publicationUid'])

        js_url_refrence = 'https://www.researchgate.net/publicliterature.PublicationCitationsList.html?publicationUid=' + id + '&useUpdatedLayoutForPublicationItems=false&loadAuthorImageLinks=false&getCommentCount=false&usePlainButton=false&useEnrichedContext=false&showAbstract=false&showType=false&showDownloadButton=false&showOpenReviewButton=false&showPublicationPreview=false&swapJournalAndAuthorPositions=false&showContexts=false&limit=10&loadMoreCount=1'
        r2 = requests.get(js_url_refrence, headers=headers)
        jsonObject = json.loads(r2.text)
        refrenceURLs = []
        refrenceIDs = []
        for refrence in jsonObject['result']['data']['citationItems']:
            refrenceURLs.append(self.baseURL + refrence['data']['url'])
            refrenceIDs.append(refrence['data']['publicationUid'])

        result = {}
        result['id'] = id
        result['title'] = title
        result['abstract'] = abstract
        result['authors'] = authorsList
        result['page'] = url
        result['cited_in'] = citedinIDs
        result['refrences'] = refrenceIDs
        result['newURLs'] = citedinURLs + refrenceURLs
        return result

    def getIDFromURL(self, url):
        return re.findall(r'publication/(?P<id>\d+)_', url)[0]

    def chceckDupURL(self, url):
        return url in self.visitedURLs

    def checkDupTitel(self, title):
        return title in self.visitedTitles

    def addLinkToQueue(self, URLList):
        self.lockQueue.acquire()
        for url in URLList:
            if not url in self.queue:
                self.queue.append(url)
        self.lockQueue.release()

    def crawlPage(self, url):
        if self.chceckDupURL(url):
            return

        parsedPage = self.parseArticlePage(url)

        if self.checkDupTitel(parsedPage['title']):
            return
        self.addLinkToQueue(parsedPage['newURLs'])

        del parsedPage['newURLs']
        file_name = '{}.json'.format(parsedPage['id'])
        with open(os.path.join(AFTER_CRAWL_BASE_DIR , file_name), 'w') as outfile:
            json.dump(parsedPage, outfile)
        self.lockAdd.acquire()
        self.numberOfVisitedPage += 1
        self.URLIDMap[parsedPage['id']] = parsedPage['page']
        self.visitedTitles.add(parsedPage['title'])
        self.visitedURLs.add(parsedPage['page'])
        self.lockAdd.release()
        #TODO : number of cited in and references

    def crawl(self, startingURL, n):
        os.makedirs(AFTER_CRAWL_BASE_DIR, exist_ok=True)
        self.n = n
        try:
            self.queue.extend(self.parseProfilePage(startingURL))
        except:
            print('cannot parse profile page')
            with open(os.path.join(AFTER_CRAWL_BASE_DIR, ERRORS_FILE_NAME), "a") as ErrorFile:
                ErrorFile.write('cannot parse profile page\n')

        threads = [CrawlThread(self) for t in range(NUMBER_OF_THREADS)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        with open(os.path.join(AFTER_CRAWL_BASE_DIR, MAP_FILE_NAME), 'w') as outfile:
            json.dump(self.URLIDMap, outfile)

    def parseProfilePage(self, url):  # return top 10 article url
        r = requests.get(url)
        s = BeautifulSoup(r.text, 'html.parser')
        articles = s.findAll('a', class_='ga-publication-item')
        result = []
        for article in articles[:10]:
            result.append(self.baseURL + article['href'])
        return result



def main():
    c = Crawler()
    url = START_PAGE
    c.crawl(url, MIN_NUMBER_OF_DOCS)


if __name__ == '__main__':
    main()
