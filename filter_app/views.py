# the view module (module with all the view functions – the ones with route() decorator)
from flask import render_template
from filter_app.app import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calc/')
def calc():
    return 'calc!'