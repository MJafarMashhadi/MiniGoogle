import json

from timer import Timer

import os
from elastic.indexing_api import IndexingAPI
from elastic.search_api import SearchAPI
from flask import Flask, render_template, redirect, url_for, request
from settings import CLUSTER_CANDIDATE_TEXT_DIRECTORY
from settings import DOCUMENTS_DIR, ELASTIC_URL, INDEX_NAME, DOCUMENT_TYPE
from settings import PORT, BIND_IP, APP_NAME, DEBUG_MODE

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

    pass


@app.route('/admin/index')
def index():
    timer = Timer()
    timer.start()
    retrieved_path = DOCUMENTS_DIR
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


def _get_cluster_data(cluster_id):
    with open(os.path.join(CLUSTER_CANDIDATE_TEXT_DIRECTORY, str(cluster_id) + '.json'), 'r') as fp:
        return json.load(fp)
    # return {"id": cluster_id, "name": "cluster {}".format(cluster_id)}


if __name__ == "__main__":
    print('starting server')
    app.run(host=BIND_IP, port=PORT)
