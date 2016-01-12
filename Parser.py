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
    
    def getPage(self, url):
        id = re.findall(r'publication/(?P<id>\d+)_',url)[0]
        print('id : ')
        print(id)
        r = requests.get(url)
        s = BeautifulSoup(r.text,'html.parser')
        title = s.find('h1',class_='pub-title')
        print('title : ')
        print(title.text)
        authors = s.findAll('a',class_='display-name')
        print('Authors :')
        for author in authors:
            print(author.text)
        abstract = s.find('div',class_='pub-abstract').div.div.text
        print('abstract : ')
        print(abstract)
    
    
        # cookies = { 'sid': r.cookies['sid'] }
        headers = {
            # 'authority': 'www.researchgate.net',
            'accept': 'application/json',
            # 'referer': url,
            'x-requested-with': 'XMLHttpRequest',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
        }
        baseURL = 'www.researchgate.net/'
    
        js_url_citedin = 'https://www.researchgate.net/publicliterature.PublicationIncomingCitationsList.html?publicationUid='+id+'&useUpdatedLayoutForPublicationItems=false&loadAuthorImageLinks=false&getCommentCount=false&usePlainButton=false&useEnrichedContext=false&showAbstract=false&showType=false&showDownloadButton=false&showOpenReviewButton=false&showPublicationPreview=false&swapJournalAndAuthorPositions=false&showContexts=false&limit=10&loadMoreCount=1'
        r2 = requests.get(js_url_citedin, headers=headers)
        jsonObject = json.loads(r2.text)
        citedinURLs = []
        for citation in jsonObject['result']['data']['citationItems']:
            citedinURLs += [baseURL+citation['data']['url']]
        print('cited in:')
        print(citedinURLs)
    
        js_url_refrence = 'https://www.researchgate.net/publicliterature.PublicationCitationsList.html?publicationUid='+id+'&useUpdatedLayoutForPublicationItems=false&loadAuthorImageLinks=false&getCommentCount=false&usePlainButton=false&useEnrichedContext=false&showAbstract=false&showType=false&showDownloadButton=false&showOpenReviewButton=false&showPublicationPreview=false&swapJournalAndAuthorPositions=false&showContexts=false&limit=10&loadMoreCount=1'
        r2 = requests.get(js_url_refrence, headers=headers)
        jsonObject = json.loads(r2.text)
        refrenceURLs = []
        for refrence in jsonObject['result']['data']['citationItems']:
            refrenceURLs += [baseURL+refrence['data']['url']]
        print('refrences :')
        print(refrenceURLs)
    
        print('bye')
        return
    
    def parse(self, url):
        id = self.getIDFromURL(url)

        r = requests.get(url)
        s = BeautifulSoup(r.text,'html.parser')
        title = s.find('h1',class_='pub-title')
        title = title.text
        authors = s.findAll('a',class_='display-name')
        authorsList=[]
        for author in authors:
            authorsList += [author.text]
        abstract = s.find('div',class_='pub-abstract').div.div.text

        headers = {
            'accept': 'application/json',
            'x-requested-with': 'XMLHttpRequest',
        }
        baseURL = 'www.researchgate.net/'

        js_url_citedin = 'https://www.researchgate.net/publicliterature.PublicationIncomingCitationsList.html?publicationUid='+id+'&useUpdatedLayoutForPublicationItems=false&loadAuthorImageLinks=false&getCommentCount=false&usePlainButton=false&useEnrichedContext=false&showAbstract=false&showType=false&showDownloadButton=false&showOpenReviewButton=false&showPublicationPreview=false&swapJournalAndAuthorPositions=false&showContexts=false&limit=10&loadMoreCount=1'
        r2 = requests.get(js_url_citedin, headers=headers)
        jsonObject = json.loads(r2.text)
        citedinURLs = []
        citedinIDs =[]
        for citation in jsonObject['result']['data']['citationItems']:
            citedinURLs.append(baseURL+citation['data']['url'])
            citedinIDs.append(citation['data']['publicationUid'])

        js_url_refrence = 'https://www.researchgate.net/publicliterature.PublicationCitationsList.html?publicationUid='+id+'&useUpdatedLayoutForPublicationItems=false&loadAuthorImageLinks=false&getCommentCount=false&usePlainButton=false&useEnrichedContext=false&showAbstract=false&showType=false&showDownloadButton=false&showOpenReviewButton=false&showPublicationPreview=false&swapJournalAndAuthorPositions=false&showContexts=false&limit=10&loadMoreCount=1'
        r2 = requests.get(js_url_refrence, headers=headers)
        jsonObject = json.loads(r2.text)
        refrenceURLs = []
        refrenceIDs = []
        for refrence in jsonObject['result']['data']['citationItems']:
            refrenceURLs.append(baseURL+refrence['data']['url'])
            refrenceIDs.append(refrence['data']['publicationUid'])

        result ={}
        result['id'] = id
        result['title'] = title
        result['abstract']=abstract
        result['authors']=authorsList
        result['page'] = url
        result['cited_in']=citedinIDs
        result['refrences']=refrenceIDs
        result['newURLs'] = citedinURLs + refrenceURLs;
        return result
    
    def getIDFromURL(self, url):
        return re.findall(r'publication/(?P<id>\d+)_',url)[0]
    
    def chceckDupURL(self, url):
        return url in self.visitedURLs
    
    def checkDupTitel(self, title):
        return title in self.visitedTitles

    def crawlPage(self, url):
        if self.chceckDupURL(url):
            return
        parsedPage = self.parse(url)
        if self.checkDupTitel(parsedPage['title']):
            return
        self.queue.extend(parsedPage['newURLs'])
        del parsedPage['newURLs']
        self.numberOfVisitedPage +=1
        self.visitedTitles.add(parsedPage['title'])
        self.visitedURLs.add(parsedPage['page'])

        with open('retrivedDocs/afterCrawl/'+parsedPage['id']+'.json', 'w') as outfile:
            json.dump(parsedPage, outfile)

    def crawl(self,startingURL , n):
        self.queue.append(startingURL)
        while self.numberOfVisitedPage < n and self.queue.count() >0 :
            self.crawlPage(self.queue.pop(0))

        with open('retrivedDocs/afterCrawl/Map.txt', 'w') as outfile:
            json.dump(self.URLIDMap, outfile)
# br  = Firefox()
# >>> br.get(url)
# >>> br.find_element_by_class_name('tab-link')
# <selenium.webdriver.remote.webelement.WebElement (session="705d09f3-d126-4ac9-9676-75bcc09a8be9", element="{88fe3c16-ef63-46da-9e65-994a9977f544}")>
# >>> b = br.find_element_by_class_name('tab-link')
# >>> b.click()
# >>> br.page_source

