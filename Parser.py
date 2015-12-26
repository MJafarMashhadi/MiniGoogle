__author__ = 'mohammad hosein'

import requests
from bs4 import BeautifulSoup
import re;

def getPage(url):
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

    return