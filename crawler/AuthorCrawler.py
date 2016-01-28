import os

from settings import AFTER_CRAWL_AUTHOR_DIR, START_PAGES, MIN_NUMBER_OF_PROFILE


__author__ = 'mohammad hosein'

import re

import requests
from bs4 import BeautifulSoup
import json


class AuthorCrawler:
    visitedProfileURL = []
    queueProfileURL = []
    visitedArticleURL = []
    queueArticleURL = []
    numberOfCrawlerProfile = 0

    def __init__(self):
        self.baseURL = 'https://www.researchgate.net/'

    def crawl(self):
        self.queueProfileURL.extend(START_PAGES)
        os.makedirs(AFTER_CRAWL_AUTHOR_DIR, exist_ok=True)
        while self.numberOfCrawlerProfile < MIN_NUMBER_OF_PROFILE:
            while len(self.queueProfileURL) == 0:
                if len(self.queueArticleURL) == 0:
                    print('finish')
                    return
                try:
                    self.queueProfileURL.extend(filter(lambda x: x not in self.visitedProfileURL and x not in self.queueProfileURL,self.getAuthorFromArticle(self.queueArticleURL.pop(0))))
                except:
                    pass
            try:
                self.crawlProfile(self.queueProfileURL.pop(0))
            except:
                pass
        print('finish')

    def getAuthorFromArticle(self, url):

        r = requests.get(url)
        s = BeautifulSoup(r.text, 'html.parser')

        authors = s.findAll('a', class_='display-name')
        authorsList = []
        for author in authors:
            authorsList.append(self.baseURL +author['href'])
        return authorsList

    def getArticleIDFromURL(self, url):
        return re.findall(r'publication/(?P<id>\d+)_', url)[0]

    def crawlProfile(self, profURL):
        if not profURL.endswith('publications'):
            profURL += '/publications'
        r = requests.get(profURL)
        s = BeautifulSoup(r.text, 'html.parser')
        name = s.find('h1', class_='profile-header-name')
        name = name.text
        n = 1
        articles = []
        while True:
            url = profURL+'/'+n.__str__()
            n+=1
            res = self.parseProfilePage(url)
            if res is None or len(res) == 0:
                break
            articles.extend(res)
        self.queueArticleURL.extend(filter(lambda x: x not in self.visitedArticleURL and x not in self.queueArticleURL,map(lambda x : x[0],articles)))
        js = {}
        js['Name'] = name
        js['Article'] = articles

        file_name = '{}.json'.format(name)
        with open(os.path.join(AFTER_CRAWL_AUTHOR_DIR , file_name), 'w') as outfile:
            json.dump(js, outfile)
        self.numberOfCrawlerProfile +=1
        print(self.numberOfCrawlerProfile)

    def parseProfilePage(self, url):  # return top 10 article url
        r = requests.get(url)
        s = BeautifulSoup(r.text, 'html.parser')
        articles = s.findAll('a', class_='ga-publication-item')
        result = []
        for article in articles:
            result.append((self.baseURL + article['href'], self.getArticleIDFromURL(article['href'])))
        return result
def main():
    c = AuthorCrawler()
    c.crawl()


if __name__ == '__main__':
    main()
