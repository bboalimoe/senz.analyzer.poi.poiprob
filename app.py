# -*- coding: utf-8 -*-

__author__ = 'jiaying.lu'

__all__ = ['app']


import os
import json
from flask import Flask
import datetime
import dao
from config import *

import logging
from logentries import LogentriesHandler

import bugsnag
from bugsnag.flask import handle_exceptions


# Configure Logentries
logger = logging.getLogger('logentries')
logger.setLevel(logging.DEBUG)
logentries_handler = LogentriesHandler(LOGENTRIES_TOKEN)
logger.addHandler(logentries_handler)

# Configure Bugsnag
bugsnag.configure(
    api_key=BUGSNAG_TOKEN,
    project_root=os.path.dirname(os.path.realpath(__file__))
)

app = Flask(__name__)

# Attach Bugsnag to Flask's exception handler
handle_exceptions(app)


@app.before_first_request
def init_before_first_request():
    init_tag = "[Initiation of Service Process]\n"
    logger.info('[init] enter init_before_first_request')

    log_init_time = "Initiation START at: \t%s\n" % (datetime.datetime.now())
    log_app_env = "Environment Variable: \t%s\n" % (APP_ENV)
    log_bugsnag_token = "Bugsnag Service TOKEN: \t%s\n" % (BUGSNAG_TOKEN)
    log_logentries_token = "Logentries Service TOKEN: \t%s\n" % (LOGENTRIES_TOKEN)
    logger.info(init_tag + log_init_time)
    logger.info(init_tag + log_app_env)
    logger.info(init_tag + log_bugsnag_token)
    logger.info(init_tag + log_logentries_token)

@app.route('/test/', methods=['GET'])
def handle_test():
    return 'haha, YES'

@app.route('/config/', methods=['GET'])
def get_config():
    return json.dumps(dao.query_config())
