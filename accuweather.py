#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Query the AccuWeather API
import os
import csv
import doctest
import json
import httplib2
import string
from datetime import date, timedelta
from optparse import OptionParser

class WeatherData:
    """ Methods for getting weather data from Accuweather.
        """

    def __init__(self, options):
        self.api_key = os.environ.get('API_KEY')
        self.api_host = os.environ.get('API_HOST')
        self.location_key = ''
        if self.api_key == None or self.api_host == None:
            raise ValueError('Both API_KEY and API_HOST environment variables must be set.')
        self.options = options

    def get(self, url):
        """ Wrapper for API requests. Take a URL, return a json array.
            """
        h = httplib2.Http('.tmp')
        (response, content) = h.request(url, "GET")
        if response['status'] != '200':
            if self.options.verbose:
                print "URL: %s" % url
            raise ValueError("AccuWeather API response: %s" % response.status)
        return json.loads(content)

    def set_location_key(self, zipcode):
        """ Set / update the location_key value.
            """
        url = 'http://%s/locations/v1/US/search?q=%s&apikey=%s' % ( self.api_host, zipcode, self.api_key )
        try:
            response = self.get(url)
        except ValueError:
            print url
        self.location_key = response[0]['Key']
        self.location = response
        return self.location_key

    def get_from_api(self, *args, **kwargs):
        """ Get data from Accuweather.
            10-day forecast: http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/daily/10day/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            1-day forecast: http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/daily/1day/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            240-hour: http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/hourly/240hour/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            72-hour: http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/hourly/72hour/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            24-hour: http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/hourly/24hour/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            12-hour: http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/hourly/12hour/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            1-hour: http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/hourly/1hour/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            Local Weather (maybe we use this instead, see what details=true gives us): http://{{api} or {{apidev}}.accuweather.com/localweather/{version}/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&getphotos=true or false}{&metric=true or false}
            Current Conditions: http://{{api} or {{apidev}}.accuweather.com/currentconditions/{version}/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&getphotos=true or false}
            """
        if self.location_key == '':
            raise ValueError("Location Key cannot be blank. Please set it with set_location_key")

        if self.options.cache == True:
            data = self.get_cache(args[0], **kwargs)
            if data != False:
                response = data
        else:
            url = 'http://%s/%s/v1/%s%s?apikey=%s%s' % ( self.api_host, kwargs['type'], kwargs['slug'], self.location_key, self.api_key, kwargs['suffix'] )
            response = self.get(url)
        self.response = response
        return response

    def get_cache(self, location, **kwargs):
        """ Get a serialized json object from the cache directory.
            """
        cachename = '%s-%s%s' % ( location.lower(), kwargs['type'], string.replace(kwargs['slug'], '/', ''))
        path = 'cache/%s.json' % cachename 
        if os.path.isfile(path) == False:
            return False
        f = open(path, 'rb')
        data = json.load(f)
        f.close()
        return data

    def write_cache(self, location, **kwargs):
        """ Cache data so we're not abusing the API.
            """
        cachename = '%s-%s%s' % ( location.lower(), kwargs['type'], string.replace(kwargs['slug'], '/', ''))
        path = 'cache/%s.json' % cachename
        f = open(path, 'wb')
        json.dump(self.response, f)
        f.close()
        return True


class PublishWeather:
    """ Methods for turning the WeatherData into something we can use.
        """

    def __init__(self, data, data_type=None):
        self.data = data
        self.limit = 0
        if data_type:
            self.data_type = data_type
            self.load_template()

    def set_limit(self, value):
        """ Set the object limit value.
            """
        self.limit = value
        return value

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
        self.slug = string.lower(string.replace(self.location, ' ', '_'))
        return value

    def load_template(self, data_type=None):
        """ Populates template var, the template depends on the data_type.
            """
        if not data_type:
            data_type = self.data_type
        path = 'html/%s.html' % data_type
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
        output = self.template

        if self.data_type == '10day':
            rows = ''
            for i, item in enumerate(self.data['DailyForecasts']):
                if i > self.limit > 0:
                    continue

                night_icon = str(item['Night']['Icon'])
                if item['Night']['Icon'] < 10:
                    night_icon = '0%s' % night_icon

                day_icon = str(item['Day']['Icon'])
                if item['Day']['Icon'] < 10:
                    day_icon = '0%s' % day_icon

                content = self.load_template('10day.row')
                content = string.replace(content, '{{high}}', str(int(item['Temperature']['Maximum']['Value'])))
                content = string.replace(content, '{{low}}', str(int(item['Temperature']['Minimum']['Value'])))
                content = string.replace(content, '{{night_icon}}', night_icon)
                content = string.replace(content, '{{day_icon}}', day_icon)
                content = string.replace(content, '{{night}}', item['Night']['IconPhrase'])
                content = string.replace(content, '{{day}}', item['Day']['IconPhrase'])
                rows += string.replace(content, '{{date}}', self.get_date(i))
            output = string.replace(output, '{{rows}}', rows)
        elif self.data_type == 'currentconditions':
            self.data = self.data[0]

            icon = str(self.data['WeatherIcon'])
            if self.data['WeatherIcon'] < 10:
                icon = '0%s' % icon
            temperature = self.data['Temperature']['Imperial']['Value']
            windchill = self.data['WindChillTemperature']['Imperial']['Value']
            precip = self.data['PrecipitationSummary']['Past24Hours']['Imperial']['Value']

            output = string.replace(output, '{{temperature}}', str(temperature))
            output = string.replace(output, '{{icon}}', icon)
            output = string.replace(output, '{{conditions}}', self.data['WeatherText'].lower())
            output = string.replace(output, '{{last24_high}}', str(int(self.data['TemperatureSummary']['Past24HourRange']['Maximum']['Imperial']['Value'])))
            output = string.replace(output, '{{last24_low}}', str(int(self.data['TemperatureSummary']['Past24HourRange']['Minimum']['Imperial']['Value'])))

            if temperature != windchill:
                output = string.replace(output, '{{windchill}}', '(Feels like %s&deg; with the wind)' % str(windchill))
            else:
                output = string.replace(output, '{{windchill}}', '')

            output = string.replace(output, '{{cloudcover}}', str(self.data['CloudCover']))

            if precip > 0.0:
                output = string.replace(output, '{{precipitation}}', '<p>Precipitation in the past 24 hours: %s"</p>' % str(precip))
            else:
                output = string.replace(output, '{{precipitation}}', '')

        # These replacements hold true for all templates
        output = string.replace(output, '{{location}}', string.replace(self.location, '+', ' '))
        output = string.replace(output, '{{slug}}', self.slug)

        self.output = output
        return output

    def get_date(self, date_offset, date_format="%a."):
        """ Helper method for taking an integer (the integer being the offset
            from the current day, where 0 = today, 1 = tomorrow etc.), and
            returning a formatted date.

            Format defaults to abbreviated weekday: "Wed."
            """
        if date_offset == 0:
            return "Today"
        return date.strftime(date.today() + timedelta(date_offset), date_format)

    def write_file(self):
        """ Write the parsed contents of a template to a file.
            """
        self.slug = self.slug.replace('+', '_')
        path = 'www/output/%s-%s.html' % ( self.data_type, self.slug )
        f = open(path, 'wb')
        f.write(self.output)
        f.close()
        return "Successfully written to %s" % path

def main(options, args):
    wd = WeatherData(options)
    if args:
        for arg in args:
            if options.verbose:
                print arg
            wd.set_location_key(arg)

            # Each data display looks something like this:
            request = { 
                'type': 'forecasts',
                'slug': 'daily/10day/',
                'suffix': ''
            }
            wd.get_from_api(arg, **request)
            wd.write_cache(arg, **request)

            pub = PublishWeather(wd.response, '10day')
            pub.set_location(arg)
            pub.write_template()
            response = pub.write_file()
            if options.verbose:
                print response

            # We also want to write a five-day version:
            pub.set_limit(5)
            #pub.write_template()
            #response = pub.write_file()
            if options.verbose:
                print response

            # ... or this:
            request = { 
                'type': 'currentconditions',
                'slug': '',
                'suffix': '&details=true'
            }
            wd.get_from_api(arg, **request)
            wd.write_cache(arg, **request)

            pub = PublishWeather(wd.response, 'currentconditions')
            pub.set_location(arg)
            pub.write_template()
            response = pub.write_file()
            if options.verbose:
                print response

            # ... or this. We should probably abstract this into a method.
            """
            request = { 
                'type': 'forecasts',
                'slug': 'hourly/24hour/',
                'suffix': ''
            }
            wd.get_from_api(arg, **request)
            wd.write_cache(arg, **request)

            pub = PublishWeather(wd.response, '24hour')
            pub.set_location(arg)
            pub.write_template()
            response = pub.write_file()
            if options.verbose:
                print response
            """


if __name__ == '__main__':
    """ Takes a list of locations, passed as args.
        Example:
        $ python accuweather.py Denver Aspen "Grand Junction"
        """
    parser = OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_option("-c", "--cache", dest="cache", default=False, action="store_true")
    (options, args) = parser.parse_args()

    if options.verbose:
        doctest.testmod(verbose=options.verbose)

    main(options, args)
