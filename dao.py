# -*- coding: utf-8 -*-

"""封装数据库操作"""

__author__ = 'jiaying.lu'
__all__ = ['CONFIG', 'GMM']

from leancloud import Object

CONFIG = Object.extend('config')
GMM = Object.extend('gmm')
