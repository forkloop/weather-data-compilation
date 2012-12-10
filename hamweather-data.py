#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
import os
import sys
import threading
from time import sleep
try:
    import requests
except ImportError:
    sys.exit('Please install `request` with `pip install requests`')

SLEEP_TIME = 9
# forecast doesn't include today
FORECAST_DAY = 7
CLIENT_ID = os.environ.get('HAMWEATHER_CLIENT_ID')
CLIENT_SECRET = os.environ.get('HAMWEATHER_CLIENT_SECRET')

OBSERVATION_END_POINT = 'http://api.aerisapi.com/observations/%s?client_id=%s&client_secret=%s' % ('%s', CLIENT_ID, CLIENT_SECRET)
FORECAST_END_POINT = 'http://api.aerisapi.com/forecasts/%s?client_id=%s&client_secret=%s' % ('%s', CLIENT_ID, CLIENT_SECRET)

DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename=(DIR + datetime.datetime.now().strftime('/ham-%Y-%m-%d-%H-%M.log')), level=logging.DEBUG)

# Load zipcodes.
with open(DIR + '/zipcode.txt') as f:
    zipcodes = [line[:5] for line in f]
zipcodes = zipcodes[:20]

def get_observation_data():
    filename = datetime.datetime.now().strftime('/ham-ob-%Y-%m-%d-%H-%M.dat')
    with open(DIR + filename, 'w') as f:
        for zipcode in zipcodes:
            url = OBSERVATION_END_POINT % zipcode
            response = requests.get(url)
            if response.status_code == requests.codes.ok:
                try:
                    json = response.json.get('response').get('ob')
                    f.write('%s, %s, %s, %s\n' % (zipcode, json.get('weather'), json.get('tempF'), json.get('humidity')))
                except:
                    logging.error(sys.exc_info()[:2])
            else:
                logging.debug(response.request.url)
                logging.error(response.text)
            sleep(SLEEP_TIME)

def get_forecast_data():
    filename = datetime.datetime.now().strftime('/ham-fc-%Y-%m-%d-%H-%M.dat')
    with open(DIR + filename, 'w') as f:
        for zipcode in zipcodes:
            url = FORECAST_END_POINT % zipcode
            response = requests.get(url)
            if response.status_code == requests.codes.ok:
                try:
                    forecast_list = response.json.get('response')[0].get('periods')
                    index = 0
                    for forecast in forecast_list:
                        if index < FORECAST_DAY:
                            index += 1
                            shifted_date = (datetime.timedelta(days=index) + datetime.datetime.now()).strftime('%Y-%m-%d')
                            f.write('%s, %s, %s, %s, %s, %s, %s\n' % (zipcode, index, shifted_date, forecast.get('maxTempF'), forecast.get('minTempF'), forecast.get('humidity'), forecast.get('weather')))
                        else:
                            break
                except:
                    logging.error(sys.exc_info()[:2])
            else:
                logging.error(response.text)
            sleep(SLEEP_TIME)

if __name__ == '__main__':
    observation_thread = threading.Thread(target=get_observation_data)
    observation_thread.start()
    forecast_thread = threading.Thread(target=get_forecast_data)
    forecast_thread.start()
