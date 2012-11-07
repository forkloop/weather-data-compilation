# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import os
import sys
import threading
from time import sleep
try:
    import requests
except ImportError:
    sys.exit('Please install `request` with `pip install requests`')

SLEEP_TIME = 5
FORECAST_DAY = 5
CLIENT_ID = os.environ.get('HAMWEATHER_CLIENT_ID')
CLIENT_SECRET = os.environ.get('HAMWEATHER_CLIENT_SECRET')

OBSERVATION_END_POINT = 'http://api.aerisapi.com/observations/%s?client_id=%s&client_secret=%s' % ('%s', CLIENT_ID, CLIENT_SECRET)
FORECAST_END_POINT = 'http://api.aerisapi.com/forecasts/%s?client_id=%s&client_secret=%s' % ('%s', CLIENT_ID, CLIENT_SECRET)

zipcodes = ()
logging.basicConfig(filename=datetime.now().strftime('ham-%Y-%m-%d-%H-%M.log'), level=logging.DEBUG)

def get_observation_data():
    filename = datetime.now().strftime('ham-ob-%Y-%m-%d-%H-%M.dat')
    with open(filename) as f:
        for zipcode in zipcodes:
            url = OBSERVATION_END_POINT % zipcode
            response = requests.get(url)
            if response.status_code == requests.codes.ok:
                json = response.json.get('ob')
                f.write('%s, %s, %s, %s\n' % (zipcode, json.get('weather'), json.get('tempF'), json.get('humidity')))
            else:
                logging.debug(response.request.url)
                logging.error(response.text)
            sleep(SLEEP_TIME)

def get_forecast_data():
    filename = datetime.now().strftime('ham-fc-%Y-%m-%d-%H-%M.dat')
    with open(filename, 'w') as f:
        for zipcode in zipcodes:
            url = FORECAST_END_POINT % zipcode
            response = requests.get(url)
            if response.status_code == requests.codes.ok:
                forecast_list = response.json.get('response')[0].get('periods')
                for forecast in forecast_list:
                    f.write('%s, %s, %s, %s, %s\n', (zipcode, forecast.get('maxTempF'), forecast.get('minTempF'), forecast.get('humidity'), forecast.get('weather')))
            else:
                logging.debug(response.request.url)
                logging.error(response.text)
            sleep(SLEEP_TIME)

if __name__ == '__main__':
    observation_thread = threading.Thread(target=get_observation_data)
    observation_thread.start()
    forecast_thread = threading.Thread(target=get_forecast_data)
    forecast_thread.start()
