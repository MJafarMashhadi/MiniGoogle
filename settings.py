import os

# General settings
RETRIEVED_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'retrievedDocs')

# Crawler settings
NUMBER_OF_THREADS = 64
START_PAGE = 'http://www.researchgate.net/researcher/8159937_Zoubin_Ghahramani'
MIN_NUMBER_OF_DOCS = 1000
AFTER_CRAWL_BASE_DIR = os.path.join(RETRIEVED_BASE_DIR, 'afterCrawl')
MAP_FILE_NAME = 'Map.txt'
ERRORS_FILE_NAME = 'ERROR.txt'

# Page Rank settings
PAGERANK_RESOURCE_DIRECTORY = AFTER_CRAWL_BASE_DIR
PAGERANK_DESTINATION_DIRECTORY = os.path.join(RETRIEVED_BASE_DIR, 'afterPageRank1')
PAGERANK_ALFA = 0.2
PAGERANK_ERROR = 1e-20

# Indexer settings
DOCUMENTS_DIR = PAGERANK_DESTINATION_DIRECTORY
ELASTIC_URL = 'http://localhost:9200/'
INDEX_NAME = 'articles'
DOCUMENT_TYPE = 'paper'

# UI settings
PORT = 5000
BIND_IP = '127.0.0.1'
APP_NAME = 'minigoogle'
DEBUG_MODE = True

# Clustering settings
CLUSTER_SOURCE_DIRECTORY = PAGERANK_DESTINATION_DIRECTORY
CLUSTER_DESTINATION_DIRECTORY = os.path.join(RETRIEVED_BASE_DIR, 'afterClustring2')
CLUSTER_CANDIDATE_TEXT_DIRECTORY = os.path.join(CLUSTER_DESTINATION_DIRECTORY,'candidateText')
CLUSTER_CANDIDATE_TEXT_LEN = 5
CLUSTER_NUM = 5
