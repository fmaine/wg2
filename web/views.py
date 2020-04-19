__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"

from markupsafe import escape
from flask import Flask
from flask import render_template
from flask import request

import os

import wg2.web.place

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

pf = wg2.web.place.PlaceFinder()

@app.route("/")
@app.route("/find")
def find():
    method = request.method
    host = request.host
    path = request.path
    args = request.args
    response = pf.find(args)
    return render_template('find.html', method=method, host=host, path=path, args=args, response=response)

@app.route("/test")
def test():
    return "This is a test"
