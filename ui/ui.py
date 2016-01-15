import json

from timer import Timer

from elastic.indexing_api import IndexingAPI
from flask import Flask, render_template, redirect, url_for
from flask import request
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
    timer = Timer()
    timer.start()
    # TODO: Do stuff here
    timer.end()
    return render_template('results.html',
        query=query_string,
        results=[],
        duration=timer.get_time_taken_pretty()
    )


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


if __name__ == "__main__":
    print('starting server')
    app.run(host=BIND_IP, port=PORT)
