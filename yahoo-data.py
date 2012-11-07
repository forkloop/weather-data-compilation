# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import sys
import xml.dom.minidom
try:
    import requests
except ImportError:
    sys.exit('Please install `requests` with `pip install requests`')

END_POINT = 'http://weather.yahooapis.com/forecastrss?w=%s'

requests_log_config = {'verbose': sys.stderr}
logging.basicConfig(filename=datetime.now().strftime('yahoo-%Y-%m-%d-%H-%M.log'), level=logging.INFO)

woeids = (2502265,)
for id in woeids:
    url = END_POINT % id
    response = requests.get(url, config=requests_log_config)
    if response.status_code == requests.codes.ok:
        try:
            weather_xml = xml.dom.minidom.parseString(response.text)
        except SyntaxError:
            print 'Oops'
            continue
        current_condition = weather_xml.getElementsByTagName('yweather:condition')[0]
        logging.info('%s, %s, %s', id, current_condition.getAttribute('text'), current_condition.getAttribute('temp'))
    else:
        print 'Oops, %s' % response.status_code
