import json

from timer import Timer

import os
from clustering.author import Author
from elastic.indexing_api import IndexingAPI
from elastic.search_api import SearchAPI
from flask import Flask, render_template, redirect, url_for, request
from settings import AUTHOR_CLUSTER_SOURCE_DIRECTORY, AUTHOR_CLUSTER_FILE
from settings import CLUSTER_CANDIDATE_TEXT_DIRECTORY
from settings import ELASTIC_URL, INDEX_NAME, DOCUMENT_TYPE, AFTER_CRAWL_BASE_DIR, PAGERANK_DESTINATION_DIRECTORY, CLUSTER_DESTINATION_DIRECTORY
from settings import PORT, BIND_IP, APP_NAME, DEBUG_MODE
from util import list_files

app = Flask(APP_NAME)
app.debug = DEBUG_MODE


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search')
def search():
    query_string = request.args.get('q')
    if not query_string or len(query_string) == 0:
        return redirect(url_for('home'))

    print('Searching for', query_string)
    api = SearchAPI(ELASTIC_URL)
    results = api.search(query_string, INDEX_NAME, DOCUMENT_TYPE, 10)
    # import random
    if 'error' not in results:
        # for r in results['hits']['hits']:
        #     r['_source']['cluster'] = random.randint(0,3)

        clusters = set(map(lambda res: res['_source']['cluster'], results['hits']['hits']))

        return render_template('results.html',
                               query=query_string,
                               total_results=results['hits']['total'],
                               results=results['hits']['hits'],
                               duration='{} seconds'.format(results['took']/1000.0),
                               topics=map(_get_cluster_data, clusters)
                               )
    else:
        return render_template('sorry.html', extra_data=json.dumps(results, indent=True))


@app.route('/search/<page>')
def search_page(page):
    page = int(page) - 1
    query_string = request.args.get('q')
    if not query_string or len(query_string) == 0:
        results = {}
    else:
        print('Searching for', query_string)
        api = SearchAPI(ELASTIC_URL)
        results = api.search(query_string, INDEX_NAME, DOCUMENT_TYPE, 10, 10*page)
        if 'error' in results:
            results = {}

    return render_template('result_items.html', results=results['hits']['hits'])


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/admin/pagerank')
def page_rank():
    timer = Timer()
    timer.start()

    from pageRank.PageRank import PageRank
    c = PageRank()
    c.pageRank()

    timer.end()

    return render_template('pagerank_result.html',
        duration=timer.get_time_taken_pretty()
    )


@app.route('/admin/cluster')
def cluster_docs():
    timer = Timer()
    timer.start()
    from clustering.K_means import K_means
    c = K_means()
    c.clusterDocs()
    timer.end()

    return render_template('clustering_result.html',
        duration=timer.get_time_taken_pretty(),
        numclusters=len(c.centroidList)
    )


@app.route('/admin/author_cluster')
def author_cluster_admin():
    timer = Timer()
    timer.start()
    authors = list()
    for file in list_files(AUTHOR_CLUSTER_SOURCE_DIRECTORY, '*.json'):
        with open(os.path.join(AUTHOR_CLUSTER_SOURCE_DIRECTORY, file), 'r') as fp:
            author_data = json.load(fp)
            authors.append(Author(author_data))

    from clustering.authors_cluster import Dendogram
    clusters = Dendogram(authors)
    clusters.cluster()

    min_similarity = 0.375
    cluster_list = list(map(
        lambda cluster: list(map(lambda x: x.name, cluster)),
        map(
            lambda x: list(x.authors),
            clusters.get_clusters(min_similarity)
        )
    ))

    cluster_dict = dict()
    for cluster in cluster_list:
        for author in cluster:
            cluster_dict[author] = cluster

    with open(AUTHOR_CLUSTER_FILE, 'w') as fp:
        json.dump(cluster_dict, fp)

    timer.end()

    return render_template('indexing_result.html',
        duration=timer.get_time_taken_pretty(),
        elastic_response=json.dumps(cluster_list, indent=True),
        success=True,
        numdocs=len(cluster_list)
    )


def _generic_index(retrieved_path):
    timer = Timer()
    timer.start()

    api = IndexingAPI(ELASTIC_URL, retrieved_path)
    response = api.bulk_add_documents_in_directory(retrieved_path, INDEX_NAME, DOCUMENT_TYPE).json()
    success = not response['errors']
    num_docs = len(response['items'])
    pretty_response = json.dumps(response, indent=True)
    timer.end()

    return render_template('indexing_result.html',
        duration=timer.get_time_taken_pretty(),
        elastic_response=pretty_response,
        success=success,
        numdocs=num_docs
    )


@app.route('/admin/index/crude')
def index():
    return _generic_index(AFTER_CRAWL_BASE_DIR)


@app.route('/admin/index/pagerank')
def index_page_rank():
    return _generic_index(PAGERANK_DESTINATION_DIRECTORY)


@app.route('/admin/index/cluster')
def index_cluster():
    return _generic_index(CLUSTER_DESTINATION_DIRECTORY)


def _get_cluster_data(cluster_id):
    with open(os.path.join(CLUSTER_CANDIDATE_TEXT_DIRECTORY, str(cluster_id) + '.json'), 'r') as fp:
        cluster_data = json.load(fp)
        cluster_data['name'] = ' '.join(cluster_data['name'])
        return cluster_data


@app.route('/author/<name>')
def get_author_cluster(name):
    with open(AUTHOR_CLUSTER_FILE) as fo:
        author_clusters = json.load(fo)

    if name in author_clusters and len(author_clusters[name]) > 1:
        return render_template('author_cluster.html', no_similar=False, cluster=author_clusters[name])
    else:
        return render_template('author_cluster.html', no_similar=True)


if __name__ == "__main__":
    print('starting server')
    app.run(host=BIND_IP, port=PORT)
