import os

# General settings
RETRIEVED_BASE_DIR = os.path.join(__path__, 'retrievedDocs')

# Crawler settings
NUMBER_OF_THREADS = 32
START_PAGE = 'http://www.researchgate.net/researcher/8159937_Zoubin_Ghahramani'
MIN_NUMBER_OF_DOCS = 1000
AFTER_CRAWL_BASE_DIR = os.path.join(RETRIEVED_BASE_DIR, 'afterCrawl')
MAP_FILE_NAME = 'Map.txt'
ERRORS_FILE_NAME = 'ERROR.txt'

# Indexer settings
DOCUMENTS_DIR = AFTER_CRAWL_BASE_DIR
ELASTIC_URL = 'http://localhost:9200/'
INDEX_NAME = 'articles'
DOCUMENT_TYPE = 'paper'
