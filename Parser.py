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




# br  = Firefox()
# >>> br.get(url)
# >>> br.find_element_by_class_name('tab-link')
# <selenium.webdriver.remote.webelement.WebElement (session="705d09f3-d126-4ac9-9676-75bcc09a8be9", element="{88fe3c16-ef63-46da-9e65-994a9977f544}")>
# >>> b = br.find_element_by_class_name('tab-link')
# >>> b.click()
# >>> br.page_source