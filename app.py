# -*- coding: utf-8 -*-

__author__ = 'jiaying.lu'

__all__ = ['app']


from flask import Flask
import datetime
from dao import *

app = Flask(__name__)


@app.route('/test/', methods=['GET'])
def handle_test():
    return 'haha, YES'

@app.route('/test/createGmm/', methods=['POST'])
def handle_create():
    gmm = GMM()
    gmm.set('description', 'test')
    gmm.set('tag', 'no-tag')
    gmm.set('timestamp', datetime.datetime.now())
    gmm.save()

    return 'save success'
