# -*- coding: utf-8 -*-
# Common package
from flask import Flask
# Personal package
import api

app = Flask(__name__)
app.register_blueprint(api.v1, url_prefix='/v1')


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
