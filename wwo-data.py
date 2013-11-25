#! /usr/bin/env python
# -*- coding: utf-8 -*-

import contextlib
import datetime
import logging
import os
import sys
from time import sleep
try:
    import requests
except ImportError:
    sys.exit('Please install `requests` with `pip install requests`')

SLEEP_TIME = 9
API_KEY = os.environ.get('WWO_API_KEY')
if API_KEY is None:
    sys.exit('Please set the `WWO_API_KEY` in your environment')

FORECAST_DAY = 15
END_POINT = 'http://api.worldweatheronline.com/premium/v1/weather.ashx?key=%s&q=%s&num_of_days=%s&format=json' % (API_KEY, '%s', FORECAST_DAY)

DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename=(DIR + datetime.datetime.now().strftime('/wwo-%Y-%m-%d-%H-%M.log')), level=logging.DEBUG)
logging.debug('pwd: ' + DIR)

# Load zipcodes.
# For zipcode startwith `0`, can not use `int` to discard the `\r\n`.
with open(DIR + '/zipcode.txt') as f:
    zipcodes = [line[:5] for line in f]
#zipcodes = zipcodes[:20]

filename_suffix = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M.dat')
with contextlib.nested(open(DIR + '/wwo-ob-' + filename_suffix, 'w'), open(DIR + '/wwo-fc-' + filename_suffix, 'w')) as (f1, f2):
    for zipcode in zipcodes:
        url = END_POINT % zipcode
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            try:
                observation = response.json().get('data').get('current_condition')[0]
                f1.write('%s, %s, %s, %s\n' % (zipcode, observation.get('weatherDesc')[0].get('value'), observation.get('temp_F'), observation.get('humidity')))
                f1.flush()
                forecast_list = response.json().get('data').get('weather')
                # 3 days forecast weather.
                # No humidity.
                index = 0
                for forecast in forecast_list:
                    # Discard the first forecast (today)
                    if index:
                        shifted_date = (datetime.timedelta(days=index) + datetime.datetime.now()).strftime('%Y-%m-%d')
                        f2.write('%s, %s, %s, %s, %s, %s\n' % (zipcode, index, shifted_date, forecast.get('maxtempF'), forecast.get('mintempF'), forecast.get('hourly')[0].get('weatherDesc')[0].get('value')))
                        f2.flush()
                    index += 1
            except:
                logging.error(sys.exc_info()[:2])
        else:
            logging.debug(response.request.url)
            logging.error(response.text)
        sleep(SLEEP_TIME)
