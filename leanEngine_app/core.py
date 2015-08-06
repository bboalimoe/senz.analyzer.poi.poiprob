# coding: utf-8

__author__ = 'jiaying.lu'

import logging
logger = logging.getLogger('logentries')

import dao
from poi_analyser_lib.predictor import Predictor
import util

def do_classify(incoming_data, x_request_id):
    '''wrapper of classify
    '''
    result = {'code': 1, 'message': ''}
    logger.debug('<%s>, [do_classify] enter, incoming_data=%s' % (x_request_id, incoming_data))

    tag = incoming_data['tag']
    seq = incoming_data['seq']
    pois = incoming_data['pois']
    algo_type = incoming_data.get('algo_type', 'gmm')
    logger.info('<%s>, [classify gmm] params: tag=%s, seq=%s, algo_type=%s' %(x_request_id, tag, seq, algo_type))

    # parse seq
    seq = [util.parse_timestamp(e) for e in seq]

    # classify
    models = []
    for poi in pois:
        try:
            model = dao.get_model_by_tag_lable(algo_type, tag, poi)
        except IndexError:
            logger.error('tag=%s, label=%s can not find model' % (tag, poi))
            result['message'] = '<%s>, [do_classify] Can not find model whose tag=%s, label=%s ' % (x_request_id ,tag, poi)
            raise ValueError(result['message'])
        models.append(model)

    _models = []
    labels = []
    for model in models:
        labels.append(model.get('eventLabel'))
        _model = {
            'nMix': model.get('nMix'),
            'covarianceType': model.get('covarianceType'),
            'nIter': model.get('nIter'),
            'count': model.get('count'),
            'params': model.get('params'),
        }
        _models.append(_model)
    my_predictor = Predictor(_models)
    logger.debug('-------\n\n_models:\n %s\n' % (_models))

    score_results = []
    seq_scores = my_predictor.scores(seq)
    logger.debug('seq_scores: %s' % (seq_scores))
    for scores in seq_scores:
        score_result = {}
        for index, score in enumerate(scores):
            if labels[index] in score_result:
                score_result[labels[index]] += score
            else:
                score_result[labels[index]] = score
        score_results.append(score_result)
    logger.debug('!!!!!! score_result:%s' %(score_result))
    # store seq in db
    for index, timestamp in enumerate(seq):
        event_label = max(score_results[index].iterkeys(), key=lambda key: score_results[index][key])  # max prob key is labelt
        dao.save_train_data(timestamp, event_label)
        logger.info('<%s> [classify] store timestamp=%s, label=%s to db success' % (x_request_id, timestamp, event_label))

    logger.info('<%s> [classify gmm] success' % (x_request_id))
    logger.debug('<%s> [classify gmm] result: %s' % (x_request_id, score_results))

    result['code'] = 0
    result['message'] = 'success'
    result['result'] = score_results

    return result


def parse_senz_pois(senz_pois_response):
    '''解析 /senz/pois/ 返回的结果，取得其中的mapping_type

    特别地，如果结果中含有home&office，也加入到pois

    Parameters
    -----
    senz_pois_response: list of dict
      e.g. dict: {"pois":[{"type": {"mapping_type":"AA"} }, {"type": {"mapping_type":"BB"} }],
                  "user_place": [{"tag":"home"}]
                 }
      parser_pois存储各类poi信息，user_place存储home&office信息

    Returns
    -----
    pois_list: list
      list of string
    '''
    senz_pois = senz_pois_response[0]
    pois = []

    if "user_place" in senz_pois and len(senz_pois["user_place"]) > 0:
        user_place = senz_pois['user_place'][0]
        if user_place['tag'] == 'home':
            pois.append('home')
        if user_place['tag'] == 'office':
            pois.append('work_office')
    print "senz_pois_response is", senz_pois_response
    for parse_pois in senz_pois['pois']:
        poi = parse_pois['type']['mapping_type']
        if poi in ['unknown', 'others', 'unkown']:
            continue
        pois.append(poi)

    return pois

