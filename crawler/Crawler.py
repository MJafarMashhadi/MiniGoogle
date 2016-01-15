import threading

__author__ = 'mohammad hosein'

import requests
from bs4 import BeautifulSoup
import re
import json


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
        result['newURLs'] = citedinURLs + refrenceURLs;
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
        with open('retrivedDocs/afterCrawl/' + parsedPage['id'] + '.json', 'w') as outfile:
            json.dump(parsedPage, outfile)
        self.lockAdd.acquire()
        self.numberOfVisitedPage += 1
        self.URLIDMap[parsedPage['id']] = parsedPage['page']
        self.visitedTitles.add(parsedPage['title'])
        self.visitedURLs.add(parsedPage['page'])
        self.lockAdd.release()

    def crawl(self, startingURL, n):
        self.n = n
        try:
            self.queue.extend(self.parseProfilePage(startingURL))
        except:
            print('cannot parse profile page')
            with open("retrivedDocs/afterCrawl/ERROR.txt", "a") as ErrorFile:
                ErrorFile.write('cannot parse profile page\n')

        numberOfThread = 16
        threads = [crawlThread(self) for t in range(numberOfThread)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        with open('retrivedDocs/afterCrawl/Map.txt', 'w') as outfile:
            json.dump(self.URLIDMap, outfile)

    def parseProfilePage(self, url):  # return top 10 article url
        r = requests.get(url)
        s = BeautifulSoup(r.text, 'html.parser')
        articles = s.findAll('a', class_='ga-publication-item')
        result = []
        for article in articles[:10]:
            result.append(self.baseURL + article['href'])
        return result


class crawlThread(threading.Thread):
    def __init__(self, c):
        threading.Thread.__init__(self)
        self.crawler = c

    def run(self):
        while self.crawler.numberOfVisitedPage < self.crawler.n and len(self.crawler.queue) > 0:
            self.crawler.lockQueue.acquire()
            currentURL = self.crawler.queue.pop(0)
            self.crawler.lockQueue.release()
            try:
                self.crawler.crawlPage(currentURL)
                print(self.crawler.numberOfVisitedPage.__str__() + ' : ' + currentURL)
            except:
                print('Error : ' + currentURL)
                with open("retrivedDocs/afterCrawl/ERROR.txt", "a") as ErrorFile:
                    ErrorFile.write(currentURL + '\n')


def main():
    c = Crawler()
    url = 'http://www.researchgate.net/researcher/8159937_Zoubin_Ghahramani'
    c.crawl(url, 1000)


if __name__ == '__main__':
    main()