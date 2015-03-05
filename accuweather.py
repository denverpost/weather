#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Query the AccuWeather API
import os
import csv
import doctest
import json
import httplib2
from optparse import OptionParser

class WeatherData:
    """ Methods for getting weather data from Accuweather.
        """

    def __init__(self):
        self.api_key = os.environ.get('API_KEY')
        self.api_host = os.environ.get('API_HOST')
        print self.api_key, self.api_host
        if self.api_key == None or self.api_host == None:
            raise ValueError('Both API_KEY and API_HOST environment variables must be set.')

    def get(self, url):
        """ Wrapper for API requests. Take a URL, return a json array.
            """
        h = httplib2.Http('.tmp')
        (response, content) = h.request(url, "GET")
        if response['status'] != '200':
            raise ValueError("AccuWeather API response: %s" % response.status)
        return json.loads(content)

    def set_location_key(self, zipcode):
        """ Set / update the location_key value.
            """
        url = 'http://%s/locations/v1/US/search?q=%s&apiKey=%s' % ( self.api_host, zipcode, self.api_key )
        response = self.get(url)
        self.location_key = response[0]['Key']
        self.location = response
        return self.location_key

    def get_forecast(self, forecast='10day'):
        """ Get the 10-day forecast.
            """
        url = 'http://%s/forecasts/v1/daily/%s/%s?apikey=%s' % ( self.api_host, forecast, self.location_key, self.api_key )
        response = self.get(url)
        self.forecast = response
        return response

class PublishWeather:
    """ Methods for turning the WeatherData into something we can use.
        """

    def __init__(self):
        pass

def main(options, args):
    wd = WeatherData()
    wd.set_location_key('Denver')
    wd.get_forecast()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true")
    (options, args) = parser.parse_args()

    if options.verbose:
        doctest.testmod(verbose=options.verbose)

    main(options, args)
