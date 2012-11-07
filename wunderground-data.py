# -*- coding: utf-8 -*-

import contextlib
from datetime import datetime
import logging
import os
import sys
from time import sleep
try:
    import requests
except ImportError:
    sys.exit('Please install `requests` with `pip install requests`')

SLEEP_TIME = 3
API_KEY = os.environ.get('WUNDERGROUND_API_KEY')
if API_KEY is None:
    sys.exit('Please set the `WUNDERGROUND_API_KEY` in your environment')

# Refer to http://www.wunderground.com/weather/api/d/docs?d=data/index
FEATURES = 'conditions/forecast'
END_POINT = 'http://api.wunderground.com/api/%s/%s/q/%s.json' % (API_KEY, FEATURES, '%s')

zipcodes = (14226, 10036, 94103)

logging.basicConfig(filename=datetime.now().strftime('wunderground-%Y-%m-%d-%H-%M.log'), level=logging.INFO)

filename_suffix = datetime.now().strftime('%Y-%m-%d-%H-%M.dat')
with contextlib.nested(open('wund-ob-' + filename_suffix, 'w'), open('wund-fc-' + filename_suffix, 'w')) as (f1, f2):
    for zipcode in zipcodes:
        url = END_POINT % zipcode
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            observation = response.json.get('current_observation')
            f1.write('%s, %s, %s\n' % (zipcode, observation.get('weather'), observation.get('temp_f')))
            forecast_list = response.json.get('forecast').get('simpleforecast').get('forecastday')
            for forecast in forecast_list:
                f2.write('%s, %s, %s, %s, %s\n' % (zipcode, forecast.get('high').get('fahrenheit'), forecast.get('low').get('fahrenheit'), forecast.get('avehumidity'), forecast.get('conditions')))
        else:
            logging.debug(response.request.url)
            logging.error(response.text)
        sleep(SLEEP_TIME)
