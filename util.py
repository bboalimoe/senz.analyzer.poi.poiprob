# coding: utf-8

__author__ = 'jiaying.lu'

import arrow

def validate_user_trace(user_trace):
    '''验证 user_trace合法性

    "user_trace": [
        {
            "timestamp": 1436486400000,
            "location": {
                "latitude": 39.987433,
                "__type": "GeoPoint",
                "longitude": 116.438513
            }
        }
    ]
    目前是 latitude, longitude 不能为同时0
    '''
    for elem in user_trace:
        if elem['location']['latitude'] == 0.0 and elem['location']['longitude'] == 0.0:
            return False

    return True


def parse_timestamp(timestamp):
    '''把输入的timestamp 减去当天的00：00的timestamp，获得一个intervening time
    '''
    today_start_arrow = arrow.get(timestamp/1000).replace(hour=0, minute=0, second=0)

    return timestamp - today_start_arrow.timestamp * 1000
