__author__ = 'jiaying.lu'

__all__ = ['APP_ID', 'MASTER_KEY', 'APP_ENV', 'LOGENTRIES_TOKEN', 'BUGSNAG_TOKEN']


import os

# for LeanEngine
APP_ID = ''
MASTER_KEY = ''

LOCAL_APP_ID = 'tzcja76flezwlklwwiaxtbgiuapyewka3bnh1ynqzlrx0rx7'
TEST_APP_ID = 'tzcja76flezwlklwwiaxtbgiuapyewka3bnh1ynqzlrx0rx7'
PROD_APP_ID = 'swgd47tvybpwkx1mzorcd16jwh2dqw4cjecxxorakn8ec3kc'

LOCAL_MASTER_KEY = '49lc8tkcuw6dlw743i4ew8sh7ioxtuh32os7cqeoeakmj85x'
TEST_MASTER_KEY = '49lc8tkcuw6dlw743i4ew8sh7ioxtuh32os7cqeoeakmj85x'
PROD_MASTER_KEY = 'aqcssgyh2lh8jay2dl3yw6dy3i3g5qwlmomhsag8ha41zl2b'

# for log & exception
LOGENTRIES_TOKEN = ''
BUGSNAG_TOKEN = ''

LOCAL_LOGENTRIES_TOKEN = 'a541fde9-100c-44b4-8784-164a697b0ab3'
TEST_LOGENTRIES_TOKEN = 'a541fde9-100c-44b4-8784-164a697b0ab3'
PROD_LOGENTRIES_TOKEN = 'f6d70f08-48a6-4e72-b722-e8b8d2d535fb'

LOCAL_BUGSNAG_TOKEN = '8d89ec939c4b02920f0c6696fad7256f'
TEST_BUGSNAG_TOKEN = '8d89ec939c4b02920f0c6696fad7256f'
PROD_BUGSNAG_TOKEN = '712e8dc9619eea3532c761830a64d9fb'

# Choose keys according to APP_ENV
if os.environ.get('LC_APP_PROD') == '1':
    # prod environ
    APP_ENV = 'prod'
elif os.environ.get('LC_APP_PROD') == '0':
    # test environ
    APP_ENV = 'test'
else:
    # dev environ
    APP_ENV = 'local'
print('-'*20 + '\n|  APP_ENV = %s |\n' %(APP_ENV) + '-'*20)
if APP_ENV == 'test':
    APP_ID = TEST_APP_ID
    MASTER_KEY = TEST_MASTER_KEY
    LOGENTRIES_TOKEN = TEST_LOGENTRIES_TOKEN
    BUGSNAG_TOKEN = TEST_BUGSNAG_TOKEN
elif APP_ENV == 'prod':
    APP_ID = PROD_APP_ID
    MASTER_KEY = PROD_MASTER_KEY
    LOGENTRIES_TOKEN = PROD_LOGENTRIES_TOKEN
    BUGSNAG_TOKEN = PROD_BUGSNAG_TOKEN
elif APP_ENV == 'local':
    APP_ID = TEST_APP_ID
    MASTER_KEY = TEST_MASTER_KEY
    LOGENTRIES_TOKEN = LOCAL_LOGENTRIES_TOKEN
    BUGSNAG_TOKEN = LOCAL_BUGSNAG_TOKEN
else:
    raise ValueError('Unvalid APP_ENV: %s' %(APP_ENV))
