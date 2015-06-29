# -*- coding: utf-8 -*-

"""封装数据库操作"""

__author__ = 'jiaying.lu'
__all__ = ['query_config']

from leancloud import Query, Object
import datetime

def query_config(config_name='pois_type'):
    '''
    query config related to poi

    Parameters
    ----------
    config_name: string

    Returns
    -------
    poi_configs: dict
    '''
    result = Query.do_cloud_query('select value from config where name="%s"' % (config_name))
    results = result.results

    if len(results) == 0:
        return {}

    poi_configs = results[0].get('value')
    return poi_configs


def save_init_gmm(tag, event_labels, n_components, covariance_type, covars_, means_):
    '''
    save init params of gmm, init num is accroding to len(event_labels)

    Parameters
    ----------
    tag: string
      gmm model's tag
    event_labels: list of string
      gmm model's label
    n_components: int
    covariance_type: string
      must in ['full', 'diag', 'tied', 'spherical']
    covars_: list of float
      len(means_) == n_components
    means_: list of float
      len(means_) == n_components

    Returns
    -------
    flag: boolean
    '''
    GMM = Object.extend('gmm')
    description = 'init save using default params'
    if covariance_type not in ['full', 'diag', 'tied', 'spherical']:
        covariance_type = 'full'
    weights_ = [1.0/n_components] * n_components
    nIter = 100

    gmm_params = {
        'nMix': n_components,
        'covarianceType': covariance_type,
        'means': means_,
        'weights': weights_,
        'nIter': nIter,
        'covars': covars_,
    }
    count = 1

    for event_label in event_labels:
        gmm = GMM()
        gmm.set('description', description)
        gmm.set('eventLabel', event_label)
        gmm.set('params', gmm_params)
        gmm.set('count', count)
        gmm.set('covarianceType', covariance_type)
        gmm.set('tag', tag)
        gmm.set('nMix', n_components)
        gmm.set('nIter', nIter)
        gmm.save()

    return True


def save_gmm(tag, event_label, description, params, count, n_iter):
    '''
    save gmm

    Parameters
    ----------
    tag: string
      gmm model's tag
    event_label: string
      gmm model's label
    description: string
      often store last model params
    params: dict
      store gmm model's full params
    count: int
      num of trained sequences
    n_iter: int
      nIter of GMM model

    Returns
    -------
    flag: boolean
    '''
    GMM = Object.extend('gmm')

    gmm = GMM()
    gmm.set('description', str(description))
    gmm.set('eventLabel', event_label)
    gmm.set('params', params)
    gmm.set('count', count)
    gmm.set('covarianceType', params['covarianceType'])
    gmm.set('tag', tag)
    gmm.set('nMix', params['nMix'])
    gmm.set('nIter', n_iter)
    gmm.save()

    return True


def get_model_by_tag(algo_type, tag):
    '''
    根据tag挑出model，如果tag下的label有重复的，选择最新的model.

    Parameters
    ----------
    algo_type: string
      model's name
    tag: string
      model's tag

    Returns
    -------
    recent_models_list: list
      list of model objs
    '''
    result = Query.do_cloud_query('select * from %s where tag="%s"' % (algo_type, tag))
    results = result.results

    # get most recent models
    models_label_set = set()
    for model in results:
        models_label_set.add(model.get('eventLabel'))

    recent_models_list = []
    for label in models_label_set:
        result = Query.do_cloud_query('select * from %s where tag="%s" and eventLabel="%s" limit 1 order by -updatedAt'
                                      % (algo_type, tag, label))
        results = result.results
        recent_models_list.append(results[0])

    return recent_models_list


def get_model_by_tag_lable(algo_type, tag, label):
    '''根据tag和label挑出model，如果tag下的label有重复的，选择最新的model.

    Parameters
    ----------
    algo_type: string
      model's name
    tag: string
      model's tag
    label: string
      model's label

    Returns
    -------
    recent_model: Obj
      model obj
    '''
    result = Query.do_cloud_query('select * from %s where tag="%s" and eventLabel="%s" limit 1 order by -updatedAt'
                                  % (algo_type, tag, label))
    results = result.results
    recent_model = results[0]

    return recent_model

def get_train_data_by_label(algo_type, label, flag):
    '''根据label 和 flag 从 algo_type 对应的表中取出训练数据

    Parameters
    ----------
    algo_type: string
      model's name
    label: string
      model's label
    flag: int
      0 untrained data, 1 all data

    Returns
    -------
    train_data: list
      list of timestamps
    '''
    algo_type_table = algo_type + 'Data'

    if flag == 0:
        result = Query.do_cloud_query('select * from %s where eventLabel="%s" and isTrain=false' %(algo_type_table, label))
    elif flag == 1:
        result = Query.do_cloud_query('select * from %s where eventLabel="%s"' %(algo_type_table, label))
    else:
        raise ValueError('flag=%s, should in [0, 1]' % (flag))

    results = result.results
    train_data = []

    for elem in results:
        train_data.append(elem.get('timestamp'))

    return train_data

