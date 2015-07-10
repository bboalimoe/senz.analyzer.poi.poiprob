# -*- coding: utf-8 -*-

__author__ = 'jiaying.lu'

__all__ = ['app']


import os
import json
from flask import Flask, request
import datetime
import arrow
import dao
import core
from config import *
from poi_analyser_lib.trainer import Trainer

import logging
from logentries import LogentriesHandler

import bugsnag
from bugsnag.flask import handle_exceptions

import requests


# Configure Logentries
logger = logging.getLogger('logentries')
if APP_ENV == 'prod':
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s : %(levelname)s, %(message)s'))
    logger.addHandler(ch)
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

@app.route('/create/', methods=['POST'])
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
    tag = 'init_model_%s000' % (arrow.now().timestamp)   # js timestamp 需要补3个0

    dao.save_init_gmm(tag, poi_configs.keys(), n_components, covariance_type, covars_, means_)

    result = {'code': 0, 'message': 'success'}
    return json.dumps(result)

@app.route('/trainRandomly/', methods=['POST'])
def train_gmm_randomly():
    '''train gmm with randomly sequences

    Parameters
    ---------
    data: JSON Obj
      e.g. {"tag":"random_train", "seq_count":30, "covariance":3600000, "algo_type":"gmm"}
      tag: string
        model's tag after train
      tag_source: string, optional, default 'init_model'
        source model's tag
      seq_count: int
        train sequence length
      covariance: float, optional, default 1000 * 60 * 60 (1 hour)
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

    tag_target = incoming_data['tag']
    tag_source = incoming_data.get('tag_source', 'init_model')
    seq_count = incoming_data['seq_count']
    covariance = incoming_data.get('covariance', 3600000)
    algo_type = incoming_data.get('algo_type', 'gmm')

    # Start train model
    poi_configs = dao.query_config()
    models = dao.get_model_by_tag(algo_type, tag_source)
    for model in models:
        label = model.get('eventLabel')
        if label.find('unknown') != -1 or label.find('others') != -1:  # ignore label `unknown`
            continue
        logger.info('<%s>, [train randomly] start train label=%s model' % (x_request_id, label))
        _model = {
            'nMix': model.get('nMix'),
            'covarianceType': model.get('covarianceType'),
            'nIter': model.get('nIter'),
            'count': model.get('count'),
            'params': model.get('params'),
        }
        my_trainer = Trainer(_model)
        my_trainer.trainRandomly(poi_configs[label]['initMeans'], seq_count, covariance)
        dao.save_gmm(tag_target, label, model.get('params'), my_trainer.modelParams(), '', model.get('count')+seq_count,
                     model.get('nIter'))

    result = {'code': 0, 'message': 'success'}
    logger.info('<%s>, [train gmm randomly] success' % (x_request_id))
    return json.dumps(result)


@app.route('/trainWithSeq/', methods=['POST'])
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
    dao.save_gmm('random_train', label, description, my_trainer.modelParams(), seq, model.get('count')+len(seq),
                 model.get('nIter'))
    result = {'code': 0, 'message': 'success'}
    logger.info('<%s>, [train gmm] success' % (x_request_id))
    logger.info('<%s>, [train gmm data] last params: %s\t train data: %s\t current params: %s'
                % (x_request_id, model.get('params'), seq, my_trainer.modelParams()))
    return json.dumps(result)


@app.route('/train/', methods=['POST'])
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
      result:
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

    poi_datas = dao.get_train_data_by_label(label, seq_type)
    seq = []
    for elem in poi_datas:
        seq.append(elem.get('timestamp'))
    model = dao.get_model_by_tag_lable(algo_type, tag, label)
    description += 'train model use datas in `poiData`, len=%s' % (len(seq))
    _model = {
        'nMix': model.get('nMix'),
        'covarianceType': model.get('covarianceType'),
        'nIter': model.get('nIter'),
        'count': model.get('count'),
        'params': model.get('params'),
    }
    my_trainer = Trainer(_model)
    my_trainer.fit(seq)
    try:
        dao.save_gmm('random_train', label, description, my_trainer.modelParams(), seq, model.get('count')+len(seq),
                     model.get('nIter'))
        result = {'code': 0, 'message': 'success'}
        logger.info('<%s>, [train gmm] success' % (x_request_id))
        logger.info('<%s>, [train gmm data] last params: %s\t train data: %s\t current params: %s'
                    % (x_request_id, model.get('params'), seq, my_trainer.modelParams()))
        poi_datas_ids = []
        for elem in poi_datas:
            poi_datas_ids.append(elem.id)
        dao.set_train_data_trained(poi_datas_ids)
        return json.dumps(result)
    except Exception:
        logger.exception('<%s>, [train gmm] oops, dao.save_gmm error' % (x_request_id))
        result['message'] = '500 Internal Server Error'
        return json.dumps(result)


@app.route('/classify/', methods=['POST'])
def classify_gmm():
    '''classify data using existing gmm model

    Parameters
    ---------
    data: JSON Obj
      e.g. {"tag":"random_train", "seq":[3600000, 50400000]}
      algo_type: string, optional, default 'gmm'
      tag: string
        model tag
      seq: list
        list of timestamps

    Returns
    -------
    result: JSON Obj
      e.g. {"code":0, "message":"success", "result":{}}
      code: int
        0 success, 1 fail
      message: string
      result: list
    '''
    if request.headers.has_key('X-Request-Id') and request.headers['X-Request-Id']:
        x_request_id = request.headers['X-Request-Id']
    else:
        x_request_id = ''

    logger.info('<%s>, [classify gmm] enter' %(x_request_id))
    result = {'code': 1, 'message': ''}

    # params JSON validate
    try:
        incoming_data = json.loads(request.data)
    except ValueError, err_msg:
        logger.exception('<%s>, [classify gmm] [ValueError] err_msg: %s, params=%s' % (x_request_id, err_msg, request.data))
        result['message'] = 'Unvalid params: NOT a JSON Object'
        return json.dumps(result)

    # params key checking
    for key in ['tag', 'seq']:
        if key not in incoming_data:
            logger.error("<%s>, [classify gmm] [KeyError] params=%s, should have key: %s" % (x_request_id, incoming_data, key))
            result['message'] = "Params content Error: can't find key=%s" % (key)
            return json.dumps(result)

    result = core.do_classify(incoming_data, x_request_id)

    return json.dumps(result)


@app.route('/locationprob/', methods=['POST'])
def location2poiprob():
    '''推测用户将去poi的可能性

    Parameters
    ---------
    data: JSON Obj
      userId: string
      user_trace: list
      dev_key: string

    Returns
    -------
    result: JSON Obj
      e.g. {"code":0, "message":"success", "result":{}}
      code: int
        0 success, 1 fail
      message: string
      result: dict
    '''
    if request.headers.has_key('X-Request-Id') and request.headers['X-Request-Id']:
        x_request_id = request.headers['X-Request-Id']
    else:
        x_request_id = ''

    logger.info('<%s>, [location2poiprob] enter' %(x_request_id))
    result = {'code': 1, 'message': ''}

    # params JSON validate
    try:
        incoming_data = json.loads(request.data)
    except ValueError, err_msg:
        logger.exception('<%s>, [location2poiprob] [ValueError] err_msg: %s, params=%s' % (x_request_id, err_msg, request.data))
        result['message'] = 'Unvalid params: NOT a JSON Object'
        return json.dumps(result)

    # params key checking
    for key in ['userId', 'user_trace', 'dev_key']:
        if key not in incoming_data:
            logger.error("<%s>, [location2poiprob] [KeyError] params=%s, should have key: %s" % (x_request_id, incoming_data, key))
            result['message'] = "Params content Error: can't find key=%s" % (key)
            return json.dumps(result)

    user_id = incoming_data['userId']
    user_trace = incoming_data['user_trace']
    dev_key = incoming_data['dev_key']
    logger.info('<%s>, [location2poiprob] params: userId=%s, user_trace=%s, dev_key=%s'
                % (x_request_id, user_id, user_trace, dev_key))

    # request senz.datasource.poi:/senz/poi/
    poi_request = {'userId': user_id, 'dev_key': dev_key, 'locations': user_trace}
    poi_response = requests.post(POI_URL, data=json.dumps(poi_request))
    if poi_response.status_code != 200:
        logger.error('<%s>, [location2poiprob] Request poi encounter %s Server Error, url=%s, request=%s'
                     % (x_request_id, poi_response.status_code, POI_URL, poi_request))
        result['message'] = 'Request poi encounter %s Server Error' % (poi_response.status_code)
        return json.dumps(result)
    poi_results = poi_response.json()
    poi_results = poi_results['results']['parse_poi']
    logger.info('<%s>, [location2poiprob] poi_url=%s, request=%s, response=%s'
                % (x_request_id, POI_URL, poi_request, poi_results))

    # request senz.datasource.poi:/senz/activities/home_office_status/
    home_office_results = []
    for geo_point in user_trace:
        # Only when it's weekday need request
        if arrow.get(geo_point['timestamp']/1000).isoweekday() > 5:
            logger.info('<%s>, [location2poiprob] timestamp=%s not in weekday' % (x_request_id, geo_point['timestamp']))
            home_office_request.append({})
            continue

        home_office_request = {'userId': user_id, 'dev_key': dev_key, 'timestamp': geo_point['timestamp'],
                            'geo_point': {'latitude': geo_point['location']['latitude'],
                                          'longitude': geo_point['location']['longitude']}}
        logger.debug('request: %s' % (json.dumps(home_office_request)))
        home_office_response = requests.post(HOME_OFFICE_URL, data=json.dumps(home_office_request))
        if home_office_response.status_code != 200:
            logger.error('<%s>, [location2poiprob] Request home_office encounter %s Server Error, url=%s, request=%s'
                         % (x_request_id, home_office_response.status_code, HOME_OFFICE_URL, home_office_request))
            result['message'] = 'Request home_office encounter %s Server Error' % (home_office_response.status_code)
            return json.dumps(result)
        home_office_result = home_office_response.json()['results']['home_office_status']
        logger.info('<%s>, [location2poiprob] home_office_url=%s, request=%s, response=%s'
                    % (x_request_id, HOME_OFFICE_URL, home_office_request, home_office_result))
        home_office_results.append(home_office_result)

    # request self:/classify/
    seq = [e['timestamp'] for e in user_trace]
    classify_request = {'tag': 'randomTrainTrial', 'seq': seq}
    classify_results = core.do_classify(classify_request, x_request_id)['result']
    logger.info('<%s>, [location2poiprob] classify request=%s, response=%s'
                % (x_request_id, classify_request, classify_results))

    # add home office status into poi prob
    poiprob_results = []
    for index in xrange(len(poi_results)):
        if home_office_results[index]:
            # 如果home_office_status有结果，则给该status 0.5的权重
            poiprob_result = dict([(key, value/2.0) for (key, value) in classify_results[index].iteritems()])
            if home_office_results[index]['at_place']['tag'] == 'home':
                poiprob_result['poi#home'] += 0.5
            if home_office_results[index]['at_place']['tag'] == 'office':
                poiprob_result['poi#work_office'] += 0.5
            poiprob_results.append(poiprob_result)
        else:
            poiprob_results.append(classify_results[index])

    # combine all results
    result['code'] = 0
    result['message'] = 'success'
    result['results'] = {'pois': poi_results, 'poiprob': poiprob_results}

    return json.dumps(result)
