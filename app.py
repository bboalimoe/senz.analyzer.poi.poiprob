# -*- coding: utf-8 -*-

__author__ = 'jiaying.lu'

__all__ = ['app']


import os
import json
from flask import Flask, request
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

@app.route('/tests/', methods=['GET'])
def handle_test():
    return 'haha, YES'

@app.route('/config/', methods=['GET'])
def get_config():
    return json.dumps(dao.query_config())

@app.route('/gmm/create/', methods=['POST'])
def create_init_gmm():
    '''create data in table `gmm` then init the params

    Parameters
    ----------
    data: JSON Obj
      e.g. {"tag":"init" , "covariance_value":1.2}
      tag: string
        tag of gmm models
      convariance_value: float
        convariance of gmm models

    Returns
    -------
    code: int
      0 success, 1 fail
    message: string
    result:
    '''
    if request.headers.has_key('X-Request-Id') and request.headers['X-Request-Id']:
        x_request_id = request.headers['X-Request-Id']
    else:
        x_request_id = ''

    logger.info('<%s>, [create gmm] enter' %(x_request_id))
    result = {'code': 1, 'message': ''}

    # params JSON validate
    try:
        incoming_data = json.loads(request.data)
    except ValueError, err_msg:
        logger.exception('<%s>, [ValueError] err_msg: %s, params=%s' % (x_request_id, err_msg, request.data))
        result['message'] = 'Unvalid params: NOT a JSON Object'
        return json.dumps(result)

    # params key checking
    for key in ['tag', 'covariance_value']:
        if key not in incoming_data:
            logger.exception("<%s>, [KeyError] params=%s, should have key: %s" % (x_request_id, incoming_data, key))
            result['message'] = "Params content Error: cant't find key=%s" % (key)
            return json.dumps(result)

    logger.info('<%s>, [create gmm] valid request with params=%s' %(x_request_id, incoming_data))

    # init gmm models
    n_components = 24
    means_ = [i*3600*1000 for i in xrange(24)]
    poi_configs = dao.query_config()
    covars_ = [incoming_data['covariance_value']] * n_components

    dao.save_init_gmm(incoming_data['tag'], poi_configs.keys(), n_components, covars_, means_)

    result = {'code': 0, 'message': 'success'}
    return json.dumps(result)
