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

    def __init__(self, options):
        self.api_key = os.environ.get('API_KEY')
        self.api_host = os.environ.get('API_HOST')
        print self.api_key, self.api_host
        if self.api_key == None or self.api_host == None:
            raise ValueError('Both API_KEY and API_HOST environment variables must be set.')
        self.options = options

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
        if self.location_key == '':
            raise ValueError("Location Key cannot be blank. Please set it with set_location_key")

        if self.options.cache == True:
            data = self.get_cache()
            if data != False:
                response = data
        else:
            url = 'http://%s/forecasts/v1/daily/%s/%s?apikey=%s' % ( self.api_host, forecast, self.location_key, self.api_key )
            response = self.get(url)
        self.response = response
        return response

    def get_cache(self, data_type='10day'):
        """ Get a serialized json object from the cache directory.
            """
        path = 'cache/%s.json' % data_type
        if os.path.isfile(path) == False:
            return False
        f = open(path, 'rb')
        data = json.load(f)
        f.close()
        return data

    def write_cache(self, response=None, data_type='10day'):
        """ Cache data so we're not abusing the API.
            """
        if response == None:
            response = self.response
        path = 'cache/%s.json' % data_type
        f = open(path, 'wb')
        json.dump(response, f)
        f.close()
        return True

class PublishWeather:
    """ Methods for turning the WeatherData into something we can use.
        """

    def __init__(self, data, data_type=None):
        self.data = data
        if data_type:
            self.data_type = data_type
            self.load_template()

    def set_data(self, value):
        """ Set the object data value.
            """
        self.data = value
        return value

    def set_data_type(self, value):
        """ Set the object data_type value.
            """
        self.data_type = value
        return value

    def set_location(self, value):
        """ Set the object location value.
            """
        self.location = value
        return value

    def load_template(self):
        """ Populates template var, the template depends on the data_type.
            """
        path = 'html/%s.html' % self.data_type
        if os.path.isfile(path) == False:
            raise ValueError("Template file %s does not exist" % path)
        f = open(path, 'rb')
        self.template = f.read()
        return self.template

    def write_template(self):
        """ Edit the template var with the values from the data var.
            """
        if self.template == '':
            raise ValueError("template var must exist and be something.")
        #path = 'mappings/%s.json' % self.data_type
        #if os.path.isfile(path) == False:
        #    raise ValueError("Mapping file %s does not exist" % path)
        #f.open(path, 'rb')
        #self.mapping = f.read()
        if self.data_type == '10day':
            for item in self.data['DailyForecasts']:
                print item

    def write_file(self):
        pass

def main(options, args):
    wd = WeatherData(options)
    location = 'Denver'
    wd.set_location_key(location)
    wd.get_forecast()
    wd.write_cache(wd.response)

    pub = PublishWeather(wd.response, '10day')

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_option("-c", "--cache", dest="cache", default=False, action="store_true")
    (options, args) = parser.parse_args()

    if options.verbose:
        doctest.testmod(verbose=options.verbose)

    main(options, args)
