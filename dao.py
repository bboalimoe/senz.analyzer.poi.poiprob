# -*- coding: utf-8 -*-

"""封装数据库操作"""

__author__ = 'jiaying.lu'
__all__ = ['query_config']

from leancloud import Object, Query

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


