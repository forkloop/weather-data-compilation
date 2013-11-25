#! /usr/bin/env python
# -*- coding: utf-8 -*-

import contextlib
import datetime
#from datetime import datetime
import logging
import os
import sys
from time import sleep
try:
    import requests
except ImportError:
    sys.exit('Please install `requests` with `pip install requests`')

SLEEP_TIME = 9
API_KEY = os.environ.get('WUNDERGROUND_API_KEY')
if API_KEY is None:
    sys.exit('Please set the `WUNDERGROUND_API_KEY` in your environment')

# Set the parameter for API request.
# Refer to http://www.wunderground.com/weather/api/d/docs?d=data/index
FEATURES = 'conditions/forecast10day'
END_POINT = 'http://api.wunderground.com/api/%s/%s/q/%s.json' % (API_KEY, FEATURES, '%s')

DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename=(DIR + datetime.datetime.now().strftime('/wunderground-%Y-%m-%d-%H-%M.log')), level=logging.DEBUG)

# Load zipcodes.
# For zipcode startwith `0`, can not use `int` to discard the `\r\n`.
with open(DIR + '/zipcode.txt') as f:
    zipcodes = [line[:5] for line in f]
#zipcodes = zipcodes[:20]

filename_suffix = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M.dat')
with contextlib.nested(open(DIR + '/wund-ob-' + filename_suffix, 'w'), open(DIR + '/wund-fc-' + filename_suffix, 'w')) as (f1, f2):
    for zipcode in zipcodes:
        url = END_POINT % zipcode
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            try:
                observation = response.json().get('current_observation')
                f1.write('%s, %s, %s, %s\n' % (zipcode, observation.get('weather'), observation.get('temp_f'), observation.get('relative_humidity')))
                f1.flush()
                forecast_list = response.json().get('forecast').get('simpleforecast').get('forecastday')
                # 3 days forecast
                index = 0
                for forecast in forecast_list:
                    # Discard the first forecast (today)
                    if index:
                        shifted_date = (datetime.timedelta(days=index) + datetime.datetime.now()).strftime('%Y-%m-%d')
                        f2.write('%s, %s, %s, %s, %s, %s, %s\n' % (zipcode, index, shifted_date, forecast.get('high').get('fahrenheit'), forecast.get('low').get('fahrenheit'), forecast.get('avehumidity'), forecast.get('conditions')))
                        f2.flush()
                    index += 1
            except:
                logging.error(sys.exc_info()[:2])
        else:
            logging.debug(response.request.url)
            logging.error(response.text)
        sleep(SLEEP_TIME)
