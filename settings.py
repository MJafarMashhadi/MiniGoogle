import os

# General settings
RETRIEVED_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'retrievedDocs')

# Crawler settings
NUMBER_OF_THREADS = 32
START_PAGE = 'http://www.researchgate.net/researcher/8159937_Zoubin_Ghahramani'
MIN_NUMBER_OF_DOCS = 1000
AFTER_CRAWL_BASE_DIR = os.path.join(RETRIEVED_BASE_DIR, 'afterCrawl')
MAP_FILE_NAME = 'Map.txt'
ERRORS_FILE_NAME = 'ERROR.txt'

# Page Rank settings
PAGERANKRESOURCEDIRECTORY = AFTER_CRAWL_BASE_DIR
PAGERANKDESTINATIONDIRECTORY = os.path.join(RETRIEVED_BASE_DIR, 'afterPageRank')
PAGERANKALFA = 0.2
PAGERANKERROR = 1e-20

# Indexer settings
DOCUMENTS_DIR = PAGERANKRESOURCEDIRECTORY
ELASTIC_URL = 'http://localhost:9200/'
INDEX_NAME = 'articles'
DOCUMENT_TYPE = 'paper'

# UI settings
PORT = 5000
BIND_IP = '127.0.0.1'
APP_NAME = 'minigoogle'
DEBUG_MODE = True