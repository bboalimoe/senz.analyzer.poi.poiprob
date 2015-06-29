# -*- coding: utf-8 -*-

__author__ = 'jiaying.lu'

__all__ = ['app']


import os
import json
from flask import Flask, request
import datetime
import dao
from config import *
from poi_analyser_lib.trainer import Trainer

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
      e.g. {"covariance_type":"full", "covariance_value":1.0, "n_components":24}
      covariance_type: string, optional default 'full'
        must in ['full', 'spherical', 'diag', 'tied']
      covariance_value: float, optional default 1.0
        covariance of gmm models
      n_components: int, optional default 24
        n_components of gmm models

    Returns
    -------
    result: JSON Obj
      e.g. {"code":0, "message":"success", "result":""}
      code: int
        0 success, 1 fail
      message: string
      result: object, optional
    '''
    if request.headers.has_key('X-Request-Id') and request.headers['X-Request-Id']:
        x_request_id = request.headers['X-Request-Id']
    else:
        x_request_id = ''

    logger.info('<%s>, [create gmm] enter' %(x_request_id))
    result = {'code': 1, 'message': ''}

    # params JSON validate
    try:
        if request.data:
            incoming_data = json.loads(request.data)
        else:
            incoming_data = {}
    except ValueError, err_msg:
        logger.exception('<%s>, [create gmm] [ValueError] err_msg: %s, params=%s' % (x_request_id, err_msg, request.data))
        result['message'] = 'Unvalid params: NOT a JSON Object'
        return json.dumps(result)

    # params key checking
    covariance_value = incoming_data.get('covariance_value', 1.0)
    covariance_type = incoming_data.get('covariance_type', 'full')
    n_components = incoming_data.get('n_components', 24)

    logger.info('<%s>, [create gmm] valid request with params=%s' %(x_request_id, incoming_data))

    # init gmm models
    means_ = [i*3600*1000 for i in xrange(24)]
    poi_configs = dao.query_config()
    covars_ = [covariance_value] * n_components
    tag = 'init_model'

    dao.save_init_gmm(tag, poi_configs.keys(), n_components, covariance_type, covars_, means_)

    result = {'code': 0, 'message': 'success'}
    return json.dumps(result)

@app.route('/gmm/trainRandomly/', methods=['POST'])
def train_gmm_randomly():
    '''train gmm with randomly sequences

    Parameters
    ---------
    data: JSON Obj
      e.g. {"tag":"init_model", "seq_count":30, "covariance":60000, "algo_type":"gmm"}
      tag: string
        model tag
      seq_count: int
        train sequence length
      covariance: float, optional, default 10*60*1000 (10 mins)
        sequence covariance. And seq means are from `config` table
      algo_type: string, optional, default 'gmm'

    Returns
    -------
    result: JSON Obj
      e.g. {"code":0, "message":"success", "result":{}}
      code: int
        0 success, 1 fail
      message: string
      result: object, optional
    '''
    if request.headers.has_key('X-Request-Id') and request.headers['X-Request-Id']:
        x_request_id = request.headers['X-Request-Id']
    else:
        x_request_id = ''

    logger.info('<%s>, [train gmm randomly] enter' %(x_request_id))
    result = {'code': 1, 'message': ''}

    # params JSON validate
    try:
        incoming_data = json.loads(request.data)
    except ValueError, err_msg:
        logger.exception('<%s>, [train gmm randomly] [ValueError] err_msg: %s, params=%s' % (x_request_id, err_msg, request.data))
        result['message'] = 'Unvalid params: NOT a JSON Object'
        return json.dumps(result)

    # params key checking
    for key in ['tag', 'seq_count']:
        if key not in incoming_data:
            logger.error("<%s>, [train gmm randomly] [KeyError] params=%s, should have key: %s" % (x_request_id, incoming_data, key))
            result['message'] = "Params content Error: can't find key=%s" % (key)
            return json.dumps(result)

    tag = incoming_data['tag']
    seq_count = incoming_data['seq_count']
    covariance = incoming_data.get('covariance', 60000)
    algo_type = incoming_data.get('algo_type', 'gmm')

    # Start train model
    poi_configs = dao.query_config()
    models = dao.get_model_by_tag(algo_type, tag)
    for model in models:
        label = model.get('eventLabel')
        _model = {
            'nMix': model.get('nMix'),
            'covarianceType': model.get('covarianceType'),
            'nIter': model.get('nIter'),
            'count': model.get('count'),
            'params': model.get('params'),
        }
        my_trainer = Trainer(_model)
        my_trainer.trainRandomly(poi_configs[label]['initMeans'], seq_count, covariance)
        dao.save_gmm('random_train', label, model.get('params'), my_trainer.modelParams(), model.get('count')+seq_count,
                     model.get('nIter'))

    result = {'code': 0, 'message': 'success'}
    logger.info('<%s>, [train gmm randomly] success' % (x_request_id))
    return json.dumps(result)


@app.route('/gmm/trainWithSeq/', methods=['POST'])
def train_gmm_with_seqs():
    '''train gmm with input sequence

    Parameters
    ---------
    data: JSON Obj
      e.g. {"tag":"init_model", "poi_label":"poi#healthcare", "seq":range(24), "description":"train demo"}
      algo_type: string, optional, default 'gmm'
      tag: string
        model tag
      poi_label: string
        model label
      seq: list
        observation sequence
      description: string
        train message

    Returns
    -------
    result: JSON Obj
      e.g. {"code":0, "message":"success", "result":{}}
      code: int
        0 success, 1 fail
      message: string
      result: object, optional
    '''
    if request.headers.has_key('X-Request-Id') and request.headers['X-Request-Id']:
        x_request_id = request.headers['X-Request-Id']
    else:
        x_request_id = ''

    logger.info('<%s>, [train gmm] enter' %(x_request_id))
    result = {'code': 1, 'message': ''}

    # params JSON validate
    try:
        incoming_data = json.loads(request.data)
    except ValueError, err_msg:
        logger.exception('<%s>, [train gmm] [ValueError] err_msg: %s, params=%s' % (x_request_id, err_msg, request.data))
        result['message'] = 'Unvalid params: NOT a JSON Object'
        return json.dumps(result)

    # params key checking
    for key in ['tag', 'poi_label', 'seq', 'description']:
        if key not in incoming_data:
            logger.error("<%s>, [train gmm] [KeyError] params=%s, should have key: %s" % (x_request_id, incoming_data, key))
            result['message'] = "Params content Error: can't find key=%s" % (key)
            return json.dumps(result)

    tag = incoming_data['tag']
    label = incoming_data['poi_label']
    seq = incoming_data['seq']
    description = incoming_data['description']
    algo_type = incoming_data.get('algo_type', 'gmm')

    model = dao.get_model_by_tag_lable(algo_type, tag, label)
    description += '\n last params: %s' % (model.get('params'))  # store last params in description
    _model = {
        'nMix': model.get('nMix'),
        'covarianceType': model.get('covarianceType'),
        'nIter': model.get('nIter'),
        'count': model.get('count'),
        'params': model.get('params'),
    }
    my_trainer = Trainer(_model)
    my_trainer.fit(seq)
    dao.save_gmm('random_train', label, description, my_trainer.modelParams(), model.get('count')+len(seq),
                 model.get('nIter'))
    result = {'code': 0, 'message': 'success'}
    logger.info('<%s>, [train gmm] success' % (x_request_id))
    logger.info('<%s>, [train gmm data] last params: %s\t train data: %s\t current params: %s'
                % (x_request_id, model.get('params'), seq, my_trainer.modelParams()))
    return json.dumps(result)


@app.route('/gmm/train/', methods=['POST'])
def train_gmm():
    '''train gmm use data in db

    Parameters
    ---------
    data: JSON Obj
      e.g. {"tag":"init_model", "poi_label":"poi#healthcare", "description":"train demo"}
      algo_type: string, optional, default 'gmm'
      tag: string
        model tag
      poi_label: string
        model label
      description: string
        train message
      seq_type: int, optional, default 0
        0 代表用未被训练的数据训练，1 代表用所有数据训练

    Returns
    -------
    result: JSON Obj
      e.g. {"code":0, "message":"success", "result":{}}
      code: int
        0 success, 1 fail
      message: string
      result: object, optional
    '''
    if request.headers.has_key('X-Request-Id') and request.headers['X-Request-Id']:
        x_request_id = request.headers['X-Request-Id']
    else:
        x_request_id = ''

    logger.info('<%s>, [train gmm] enter' %(x_request_id))
    result = {'code': 1, 'message': ''}

    # params JSON validate
    try:
        incoming_data = json.loads(request.data)
    except ValueError, err_msg:
        logger.exception('<%s>, [train gmm] [ValueError] err_msg: %s, params=%s' % (x_request_id, err_msg, request.data))
        result['message'] = 'Unvalid params: NOT a JSON Object'
        return json.dumps(result)

    # params key checking
    for key in ['tag', 'poi_label', 'description']:
        if key not in incoming_data:
            logger.error("<%s>, [train gmm] [KeyError] params=%s, should have key: %s" % (x_request_id, incoming_data, key))
            result['message'] = "Params content Error: can't find key=%s" % (key)
            return json.dumps(result)

    tag = incoming_data['tag']
    label = incoming_data['poi_label']
    description = incoming_data['description']
    algo_type = incoming_data.get('algo_type', 'gmm')
    seq_type = incoming_data.get('seq_type', 0)

    seq = dao.get_train_data_by_label(algo_type, label, seq_type)
    model = dao.get_model_by_tag_lable(algo_type, tag, label)
    description += '\n last params: %s' % (model.get('params'))  # store last params in description
    _model = {
        'nMix': model.get('nMix'),
        'covarianceType': model.get('covarianceType'),
        'nIter': model.get('nIter'),
        'count': model.get('count'),
        'params': model.get('params'),
    }
    my_trainer = Trainer(_model)
    my_trainer.fit(seq)
    dao.save_gmm('random_train', label, description, my_trainer.modelParams(), model.get('count')+len(seq),
                 model.get('nIter'))
    result = {'code': 0, 'message': 'success'}
    logger.info('<%s>, [train gmm] success' % (x_request_id))
    logger.info('<%s>, [train gmm data] last params: %s\t train data: %s\t current params: %s'
                % (x_request_id, model.get('params'), seq, my_trainer.modelParams()))
    return json.dumps(result)

