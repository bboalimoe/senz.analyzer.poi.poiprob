# -*- coding: utf-8 -*-

__author__ = 'jiaying.lu'

__all__ = ['app']

import os
import json
import datetime
import logging

from flask import Flask, request, make_response
import arrow
from logentries import LogentriesHandler
import bugsnag
from bugsnag.flask import handle_exceptions
import requests

import dao
import core
import util
from config import *
from poi_analyser_lib.trainer import Trainer




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
        result['code'] = 103
        return make_response(json.dumps(result), 400)

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
      e.g. {"sourceTag":"init_model_timestamp", "covariance":3600000, "algo_type":"gmm"}
      sourceTag: string
        source model's tag
      targetTag: string, optional, default 'randomTrain'
        model's tag after train
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
        result['code'] = 103
        return make_response(json.dumps(result), 400)

    # params key checking
    for key in ['sourceTag']:
        if key not in incoming_data:
            logger.error("<%s>, [train gmm randomly] [KeyError] params=%s, should have key: %s" % (x_request_id, incoming_data, key))
            result['message'] = "Params content Error: can't find key=%s" % (key)
            result['code'] = 103
            return make_response(json.dumps(result), 400)

    source_tag = incoming_data['sourceTag']
    target_tag = incoming_data.get('targetTag', 'randomTrain')
    covariance = incoming_data.get('covariance', 3600000)
    algo_type = incoming_data.get('algo_type', 'gmm')

    # Start train model
    poi_configs = dao.query_config()
    models = dao.get_model_by_tag(algo_type, source_tag)
    if len(models) < 1:
        logger.info('<%s> [train gmm randomly] sourceTag=%s query empty result'
                    % (x_request_id, source_tag))
        result['message'] = 'sourceTag=%s query empty result' % (source_tag)
        return json.dumps(result)
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
        # TODO: do this in db, not in code
        seq_count = poi_configs[label]['count'] * 10   # read from db, need > 24 n_component
        my_trainer.trainRandomly(poi_configs[label]['initMeans'], seq_count, covariance)
        dao.save_gmm(target_tag, label, model.get('params'), my_trainer.modelParams(), '',
                     model.get('count')+seq_count, model.get('nIter'))

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
      e.g. {"tag":"random_train", "seq":[3600000, 50400000], "pois":["home", "ktv"]}
      algo_type: string, optional, default 'gmm'
      tag: string
        model tag
      seq: list
        list of timestamps
      pois: list
        list of poi labels

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
    for key in ['tag', 'seq', 'pois']:
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
        current please use `senz`
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
        result['code'] = 103
        return make_response(json.dumps(result), 400)

    # params key checking
    for key in ['userId', 'user_trace', 'dev_key']:
        if key not in incoming_data:
            logger.error("<%s>, [location2poiprob] [KeyError] params=%s, should have key: %s" % (x_request_id, incoming_data, key))
            result['message'] = "Params content Error: can't find key=%s" % (key)
            result['code'] = 103
            return make_response(json.dumps(result), 400)

    user_id = incoming_data['userId']
    user_trace = incoming_data['user_trace']
    dev_key = incoming_data['dev_key']
    logger.info('<%s>, [location2poiprob] params: userId=%s, user_trace=%s, dev_key=%s'
                % (x_request_id, user_id, user_trace, dev_key))

    # validate user_trace
    if not util.validate_user_trace(user_trace):
        result['message'] = "Unvalid user_trace: %s" % (user_trace)
        result['code'] = 103
        return make_response(json.dumps(result), 400)

    # request senz.datasource.poi:/senz/poi/
    poi_request = {'userId': user_id, 'dev_key': dev_key, 'locations': user_trace}
    poi_response = requests.post(POI_URL, data=json.dumps(poi_request))
    if poi_response.status_code != 200:
        logger.error('<%s>, [location2poiprob] Request poi encounter %s Server Error, url=%s, request=%s'
                     % (x_request_id, poi_response.status_code, POI_URL, poi_request))
        result['message'] = 'Request poi encounter %s Server Error' % (poi_response.status_code)
        result['code'] = 302
        return make_response(json.dumps(result), 500)
    poi_results = poi_response.json()
    poi_results = poi_results['results']['parse_poi']
    logger.info('<%s>, [location2poiprob] poi_url=%s, request=%s, response=%s'
                % (x_request_id, POI_URL, poi_request, poi_results))

    # parse poi_results
    pois = core.parse_senz_pois(poi_results)
    if len(pois) == 0:
        result['message'] = "Pois = NULL, Please check request params"
        result['code'] = 102
        return make_response(json.dumps(result), 500)


    # request self:/classify/
    seq = [e['timestamp'] for e in user_trace]
    classify_request = {'tag': 'randomTrain', 'seq': seq, 'pois': pois}  # TODO: 每次从哪种tag中取, 比如从最近有更新的地方
    try:
        classify_results = core.do_classify(classify_request, x_request_id)['result']
    except ValueError, err:
        result['message'] = err.message
        return make_response(json.dumps(result), 500)
    logger.info('<%s>, [location2poiprob] classify request=%s, response=%s'
                % (x_request_id, classify_request, classify_results))

    # poiprob_results map with `DEFAULT_POI_MAPPING`
    map_poiprob_results = []
    for poiprob_result in classify_results:
        map_poiprob_result = {}
        for level2_poi, poiprob in poiprob_result.iteritems():
            level1_poi = DEFAULT_POI_MAPPING[level2_poi]
            if level1_poi not in map_poiprob_result:
                map_poiprob_result[level1_poi] = {'level1_prob': 0.0, 'level2_prob': {}}
            map_poiprob_result[level1_poi]['level1_prob'] += poiprob
            map_poiprob_result[level1_poi]['level2_prob'][level2_poi] = poiprob
        map_poiprob_results.append(map_poiprob_result)

    # combine all results
    result['code'] = 0
    result['message'] = 'success'
    result['results'] = {'pois': poi_results, 'poi_probability': map_poiprob_results}

    return json.dumps(result)

