from random import randint

from flask import Flask, render_template
from flask import request

app = Flask('minigoogle')
# app = Flask(__name__)
app.debug = True


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search')
def search():
    query_string = request.args.get('q')
    print (query_string)
    return render_template('results.html', 
        query=query_string,
        results=[],
        duration=randint(1,100)/100.0
    )


if __name__ == "__main__":
    print('starting server')
    app.run()
