__author__ = 'mohammad hosein'

import json
import threading
import os
import re

import requests
from bs4 import BeautifulSoup

from settings import NUMBER_OF_THREADS, START_PAGES, MIN_NUMBER_OF_DOCS, \
    MAP_FILE_NAME, ERRORS_FILE_NAME, AFTER_CRAWL_BASE_DIR, CITEDIN_NUMBER, REFRENCES_NUMBER
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
        id = self.getArticleIDFromURL(url)

        r = requests.get(url)
        s = BeautifulSoup(r.text, 'html.parser')

        # type_ = s.find('div',class_='type-label')
        # t= type_.text.replace(' ', '')
        # if t != 'Article':
        #     raise Exception()

        title = s.find('h1', class_='pub-title')
        title = title.text
        authors = s.findAll('a', class_='display-name')
        authorsList = []
        for author in authors:
            authorsList.append((self.getAuthorIDFromURL(author['href']) ,author.text,self.baseURL +author['href']))
        abstract = s.find('div', class_='pub-abstract').div.div.text

        headers = {
            'accept': 'application/json',
            'x-requested-with': 'XMLHttpRequest',
        }

        js_url_citedin = 'https://www.researchgate.net/publicliterature.PublicationIncomingCitationsList.html?publicationUid=' + id + '&useUpdatedLayoutForPublicationItems=false&loadAuthorImageLinks=false&getCommentCount=false&usePlainButton=false&useEnrichedContext=false&showAbstract=false&showType=false&showDownloadButton=false&showOpenReviewButton=false&showPublicationPreview=false&swapJournalAndAuthorPositions=false&showContexts=false&limit=10000'
        r2 = requests.get(js_url_citedin, headers=headers)
        jsonObject = json.loads(r2.text)
        citedinURLs = []
        citedinIDs = []
        c=0
        for citation in jsonObject['result']['data']['citationItems']:
            if c < CITEDIN_NUMBER :
                c+=1
                citedinURLs.append(self.baseURL + citation['data']['url'])
            citedinIDs.append(citation['data']['publicationUid'])
        citedinURLs = citedinURLs[:10]

        js_url_refrence = 'https://www.researchgate.net/publicliterature.PublicationCitationsList.html?publicationUid=' + id + '&useUpdatedLayoutForPublicationItems=false&loadAuthorImageLinks=false&getCommentCount=false&usePlainButton=false&useEnrichedContext=false&showAbstract=false&showType=false&showDownloadButton=false&showOpenReviewButton=false&showPublicationPreview=false&swapJournalAndAuthorPositions=false&showContexts=false&limit=10000'
        r2 = requests.get(js_url_refrence, headers=headers)
        jsonObject = json.loads(r2.text)
        refrenceURLs = []
        refrenceIDs = []
        c = 0
        for refrence in jsonObject['result']['data']['citationItems']:
            if c < REFRENCES_NUMBER :
                refrenceURLs.append(self.baseURL + refrence['data']['url'])
                c +=1
            refrenceIDs.append(refrence['data']['publicationUid'])
        # refrenceURLs = refrenceURLs[:10]

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

    def getArticleIDFromURL(self, url):
        return re.findall(r'publication/(?P<id>\d+)_', url)[0]
    def getAuthorIDFromURL(self,url):
        try:
            return re.findall(r'researcher/(?P<id>\d+)_', url)[0]
        except:
            try:
                return re.findall(r'profile/(?P<id>\d+)_', url)[0]
            except:
                return '0'


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
        if parsedPage is None:
            return

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

    def crawl(self):
        n = MIN_NUMBER_OF_DOCS
        startingURL = START_PAGES
        os.makedirs(AFTER_CRAWL_BASE_DIR, exist_ok=True)
        self.n = n
        for sURL in startingURL:
            try:
                self.queue.extend(self.parseProfilePage(sURL))
            except:
                print('cannot parse profile page')
                with open(os.path.join(AFTER_CRAWL_BASE_DIR, ERRORS_FILE_NAME), "a") as ErrorFile:
                    ErrorFile.write('cannot parse profile page ',sURL,'\n')

        threads = [CrawlThread(self) for t in range(NUMBER_OF_THREADS)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        with open(os.path.join(AFTER_CRAWL_BASE_DIR, MAP_FILE_NAME), 'w') as outfile:
            json.dump(self.URLIDMap, outfile)
        print('End Crawling!')

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
    c.crawl()


if __name__ == '__main__':
    main()
