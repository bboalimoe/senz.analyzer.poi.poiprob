__author__ = 'jiaying.lu'

__all__ = ['APP_ID', 'MASTER_KEY', 'APP_ENV', 'LOGENTRIES_TOKEN', 'BUGSNAG_TOKEN',
           'POI_URL', 'PLACE_URL', 'HOME_OFFICE_URL', 'DEFAULT_POI_MAPPING']

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
'''
# for leanEngine
if os.environ.get('LC_APP_PROD') == '1':
    # prod environ
    APP_ENV = 'prod'
elif os.environ.get('LC_APP_PROD') == '0':
    # test environ
    APP_ENV = 'test'
else:
    # dev environ
    APP_ENV = 'local'
'''
try:
    APP_ENV = os.environ["APP_ENV"]
except KeyError, key:
    print "KeyError: There is no env var named %s" % key
    print "The local env will be applied"
    APP_ENV = "local"

print('-' * 20 + '\n|  APP_ENV = %s |\n' % (APP_ENV) + '-' * 20)
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
    raise ValueError('Unvalid APP_ENV: %s' % (APP_ENV))


# for POST urls
#POI_URL = 'http://senz-test-senz-datasource-poi.daoapp.io/senz/pois/'
#PLACE_URL = 'http://senz-test-senz-datasource-poi.daoapp.io/senz/places/'
#HOME_OFFICE_URL = 'http://senz-test-senz-datasource-poi.daoapp.io/senz/activities/home_office_status/'
POI_URL = 'http://senz-senz-datasource-poi.daoapp.io/senz/pois/'
PLACE_URL = 'http://senz-senz-datasource-poi.daoapp.io/senz/places/'
HOME_OFFICE_URL = 'http://senz-senz-datasource-poi.daoapp.io/senz/activities/home_office_status/'

# TODO: DEFAULT_MAP need read from db
# poi level1 to level2 map
RAW_POI_MAPPING = {
    'dining': [
        'chinese_restaurant', 'japan_korea_restaurant', 'western_restaurant', 'bbq', 'chafing_dish', 'seafood',
        'vegetarian_diet', 'muslim', 'buffet', 'dessert', 'cooler', 'snack_bar',
    ],
    'shopping': [
        'comprehensive_market', 'convenience_store', 'supermarket', 'digital_store', 'pet_market', 'furniture_store',
        'farmers_market', 'commodity_market', 'flea_market', 'sports_store', 'clothing_store', 'video_store',
        'glass_store', 'mother_store', 'jewelry_store', 'cosmetics_store', 'gift_store', 'photography_store',
        'pawnshop', 'antique_store', 'bike_store', 'cigarette_store', 'stationer',
    ],
    'life_service': [
        'travel_agency', 'ticket_agent', 'post_office', 'telecom_offices', 'newstand', 'water_supply_office',
        'electricity_office', 'photographic_studio', 'laundry', 'talent_market', 'lottery_station', 'housekeeping',
        'intermediary', 'pet_service', 'salvage_station', 'welfare_house', 'barbershop',
    ],
    'entertainment': [
        'bath_sauna', 'ktv', 'bar', 'coffee', 'night_club', 'cinema', 'odeum', 'resort', 'outdoor', 'game_room',
        'internet_bar',
    ],
    'auto_related': [
        'gas_station', 'parking_plot', 'auto_sale', 'auto_repair', 'motorcycle', 'car_maintenance', 'car_wash',
    ],
    'healthcare': [
        'hospital', 'clinic', 'emergency_center', 'drugstore',
    ],
    'hotel': [
        'motel', 'hotel', 'economy_hotel', 'guest_house', 'hostel',
    ],
    'scenic_spot': ['scenic_spot'
                    ],
    'exhibition': [
        'museum', 'exhibition_hall', 'science_museum', 'library', 'gallery', 'convention_center',
    ],
    'education': [
        'university', 'high_school', 'primary_school', 'kinder_garten', 'training_institutions', 'technical_school',
        'adult_education',
    ],
    'finance': [
        'bank', 'atm', 'insurance_company', 'security_company',
    ],
    'infrastructure': [
        'traffic', 'public_utilities', 'toll_station', 'other_infrastructure',
    ],
    'estate': [
        'residence', 'business_building'
    ],
    'home': ['home'],
    'office': ['work_office'],
}

# poi level2 to level1 map
DEFAULT_POI_MAPPING = {}
for level1_poi in RAW_POI_MAPPING:
    for levele2_poi in RAW_POI_MAPPING[level1_poi]:
        DEFAULT_POI_MAPPING[levele2_poi] = level1_poi
print('DEFAULT_POI_MAP=\n%s' % (DEFAULT_POI_MAPPING))
