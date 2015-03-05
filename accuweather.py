#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Query the AccuWeather API
import os
import csv
import doctest
import httplib2
from optparse import OptionParser

class WeatherData:

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
        print response
        print '==========='
        return content

    def set_location_key(self, zipcode):
        """ Set / update the location_key value.
            """
        url = 'http://%s/locations/v1/US/search?q=%s&apiKey=%s' % ( self.api_host, zipcode, self.api_key )
        location_key = self.get(url)
        print location_key

def main(options, args):
    wd = WeatherData()
    wd.set_location_key('80203')

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true")
    (options, args) = parser.parse_args()

    if options.verbose:
        doctest.testmod(verbose=options.verbose)

    main(options, args)
