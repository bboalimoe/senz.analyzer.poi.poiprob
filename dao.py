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

    poi_configs = results[0].get('value')

    return poi_configs


def save_init_gmm(tag, event_labels, n_components, covars_, means_):
    '''
    save init params of gmm, init num is accroding to len(event_labels)

    Parameters
    ----------
    tag: string
      gmm model's tag
    event_labels: list of string
      gmm model's label
    n_components: int
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
    covariance_type = 'full'
    gmm_params = {
        'nMix': n_components,
        'covarianceType': covariance_type,
        'means': means_,
        'covars': covars_
    }
    count = 0

    for event_label in event_labels:
        gmm = GMM()
        gmm.set('description', description)
        gmm.set('eventLabel', event_label)
        gmm.set('params', gmm_params)
        gmm.set('count', count)
        gmm.set('covarianceType', covariance_type)
        gmm.set('tag', tag)
        gmm.set('nMix', n_components)
        gmm.set('timestamp', datetime.datetime.now())
        gmm.save()

    return True
