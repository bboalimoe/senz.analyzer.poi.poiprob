__author__ = 'jiaying.lu'

__all__ = ['APP_ID', 'MASTER_KEY', 'APP_ENV']


import os

APP_ID = ''
MASTER_KEY = ''

LOCAL_APP_ID = 'tzcja76flezwlklwwiaxtbgiuapyewka3bnh1ynqzlrx0rx7'
TEST_APP_ID = 'tzcja76flezwlklwwiaxtbgiuapyewka3bnh1ynqzlrx0rx7'
PROD_APP_ID = 'swgd47tvybpwkx1mzorcd16jwh2dqw4cjecxxorakn8ec3kc'

LOCAL_MASTER_KEY = '49lc8tkcuw6dlw743i4ew8sh7ioxtuh32os7cqeoeakmj85x'
TEST_MASTER_KEY = '49lc8tkcuw6dlw743i4ew8sh7ioxtuh32os7cqeoeakmj85x'
PROD_MASTER_KEY = 'aqcssgyh2lh8jay2dl3yw6dy3i3g5qwlmomhsag8ha41zl2b'

# Choose keys according to APP_ENV
try:
    APP_ENV = os.environ['APP_ENV']
except KeyError, key:
    print("KeyError: There's no evn var named %s" % (key))
    print("The local env will be applied")
    APP_ENV = 'local'
finally:
    if APP_ENV == 'test':
        APP_ID = TEST_APP_ID
        MASTER_KEY = TEST_MASTER_KEY
    elif APP_ENV == 'prod':
        APP_ID = PROD_APP_ID
        MASTER_KEY = PROD_MASTER_KEY
    elif APP_ENV == 'local':
        APP_ID = TEST_APP_ID
        MASTER_KEY = TEST_MASTER_KEY
    else:
        raise ValueError('Unvalid APP_ENV: %s' %(APP_ENV))
