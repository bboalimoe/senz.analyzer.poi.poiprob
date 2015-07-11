# coding: utf-8

__author__ = 'jiaying.lu'

import logging
logger = logging.getLogger('logentries')

import dao
from poi_analyser_lib.predictor import Predictor

def do_classify(incoming_data, x_request_id):
    '''wrapper of classify
    '''
    result = {'code': 1, 'message': ''}
    logger.debug('<%s>, [do_classify] enter, incoming_data=%s' % (x_request_id, incoming_data))

    tag = incoming_data['tag']
    seq = incoming_data['seq']
    algo_type = incoming_data.get('algo_type', 'gmm')
    logger.info('<%s>, [classify gmm] params: tag=%s, seq=%s, algo_type=%s' %(x_request_id, tag, seq, algo_type))

    # classify
    models = dao.get_model_by_tag(algo_type, tag)
    if not models:
        result['message'] = "There's no model's tag=%s" % (tag)
        logger.info('<%s>, [classify] request not exist model tag=%s' % (x_request_id, tag))
        return result

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

    score_results = []
    seq_scores = my_predictor.scores(seq)
    for scores in seq_scores:
        score_result = {}
        for index, score in enumerate(scores):
            score_result[labels[index]] = score
        score_results.append(score_result)
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
