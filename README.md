Google(mini)
============

3rd Project of [Modern Information Retrieval](http://ce.sharif.edu/courses/94-95/1/ce324-1/) course.

Crawls research gate and indexes papers in the site. Clusters papers, authors and calculates rank for papers based on their citation and references.

Crawler is written from scratch. Indexing and retrieval is done with [elastic search 2.1](https://elastic.co), web interface is powered by [flask](flask.pocoo.org) and [bootstrap](http://getbootstrap.com), [numpy](http://numpy.org) helps a lot in performing ranking and clustering calculations.

How to use
==========

Install requirements from requirements.txt file. Creating a python virtual environment is a really good idea.

    pip install -r requirements.txt
    python ui/ui.py  # requires python3.4 or higher

And open [http://127.0.0.1:5000/admin/](http://127.0.0.1:5000/admin/) in your browser. Crawl, calculate page ranks, perform clustering and finally add documents to index. Now your mini version of google can  be used. Just point your browser to [http://127.0.0.1:5000/search](http://127.0.0.1:5000/search).

**Note:** You should setup elastic search before adding documents to index. For more information read [here](https://www.elastic.co/downloads/elasticsearch)

Contributors
============

* [Mohammad Hossein Sharafi](http://ce.sharif.edu/~mhsharafi)
* [Mohammad Jafar Mashhadi](http://ce.sharif.edu/~mjmashhadiebrahim)