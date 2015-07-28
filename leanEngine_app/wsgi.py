# -*- coding: utf-8 -*-
__author__ = 'jiaying.lu'

import leancloud
from wsgiref import simple_server

from config import *
from app import app
from gevent import monkey

monkey.patch_all()

leancloud.init(APP_ID, master_key=MASTER_KEY)

application = leancloud.Engine(app)


if __name__ == '__main__':
    # 只在本地开发环境执行的代码
    app.debug = True
    server = simple_server.make_server('0.0.0.0', 9010, application)
    server.serve_forever()
