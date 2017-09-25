#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Query the AccuWeather API
import os
import csv
import doctest
import json
import httplib2
from FtpWrapper import FtpWrapper
import string
import argparse
from datetime import date, timedelta

class WeatherData:
    """ Methods for getting weather data from Accuweather.
        """

    def __init__(self, args):
        self.api_key = os.environ.get('API_KEY')
        self.api_host = os.environ.get('API_HOST')
        self.location_key = ''
        if self.api_key == None or self.api_host == None:
            raise ValueError('Both API_KEY and API_HOST environment variables must be set.')
        self.args = args

    def get(self, url):
        """ Wrapper for API requests. Take a URL, return a json array.
            """
        h = httplib2.Http('.tmp')
        (response, content) = h.request(url, "GET")
        if response['status'] != '200':
            if self.args.verbose:
                print "URL: %s" % url
            raise ValueError("AccuWeather API response: %s" % response.status)
        try:
            return json.loads(content)
        except:
            print content

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
            FORECASTS:
            10-day forecast
                http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/daily/10day/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            1-day forecast
                http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/daily/1day/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            240-hour
                http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/hourly/240hour/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            72-hour
                http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/hourly/72hour/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            24-hour
                http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/hourly/24hour/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            12-hour
                http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/hourly/12hour/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            1-hour
                http://{{api} or {{apidev}}.accuweather.com/forecasts/{version}/hourly/1hour/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&metric={true or false}}
            Local Weather (maybe we use this instead, see what details=true gives us)
                http://{{api} or {{apidev}}.accuweather.com/localweather/{version}/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&getphotos=true or false}{&metric=true or false}
            Current Conditions
                http://{{api} or {{apidev}}.accuweather.com/currentconditions/{version}/{locationKey}{.{format}}?apikey={your key}{&language={language code}}{&details={true or false}}{&getphotos=true or false}

            CLIMATOLOGICAL / HISTORICAL:
            Climo Actuals For Month or Day By Location Key 
                http://{{api} or {{apidev}}.accuweather.com/climo/{version}/actuals/yyyy/mm/{dd}/{locationKey}{.{format}}?apikey={your key}
                http://api.accuweather.com/climo/v1/actuals/2012/12/17/350540?apikey={your key} 
            Climo Records For Month or Day By Location Key
                http://{{api} or {{apidev}}.accuweather.com/climo/{version}/records/yyyy/mm/{dd}/{locationKey}{.{format}}?apikey={your key}
                http://api.accuweather.com/climo/v1/records/2012/12/15/350540?apikey={your key}
            Climo Normals For Month or Day By Location Key 
                http://{{api} or {{apidev}}.accuweather.com/climo/{version}/normals/yyyy/mm/{dd}/{locationKey}{.{format}}?apikey={your key}
                http://api.accuweather.com/climo/v1/normals/2012/12/25/350540?apikey={your key}
            Climo Month Summary By Location Key 
                http://{{api} or {{apidev}}.accuweather.com/climo/{version}/summary/yyyy/mm/{locationKey}{.{format}} ? details={true/false} & apikey={your key}
                http://api.accuweather.com/climo/v1/summary/2014/02/350540?apikey={your key}    

            """
        if self.location_key == '':
            raise ValueError("Location Key cannot be blank. Please set it with set_location_key")

        cache = False
        if 'cache' in self.args and self.args.cache is True:
            cache = True
            data = self.get_cache(args[0], **kwargs)
            if data != False:
                response = data
        else:
            url = 'http://%s/%s/v1/%s%s?apikey=%s%s' % ( self.api_host, kwargs['type'], kwargs['slug'], self.location_key, self.api_key, kwargs['suffix'] )
            response = self.get(url)

        if self.args.verbose:
            print "From cache: %r" % cache
            print "API Response: %s" % response

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


class LogWeather:
    """ Methods for keeping track of WeatherData over a day.
        We only use this with a location's currentconditions.
        Data logged: Cloudiness, highs, lows, precipitation.
        """

    def __init__(self, data):
        self.data = data

    def set_data(self, value):
        """ Set the object data value.
            """
        self.data = value
        return value


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
        # The template is loaded in the init method.
        if self.template == '':
            raise ValueError("template var must exist and be something.")
        output = self.template

        if self.data_type in ['10day', '5day']:
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

            output = string.replace(output, '{{temperature}}', str(int(temperature)))
            output = string.replace(output, '{{icon}}', icon)
            output = string.replace(output, '{{conditions}}', self.data['WeatherText'].lower())
            output = string.replace(output, '{{last24_high}}', str(int(self.data['TemperatureSummary']['Past24HourRange']['Maximum']['Imperial']['Value'])))
            output = string.replace(output, '{{last24_low}}', str(int(self.data['TemperatureSummary']['Past24HourRange']['Minimum']['Imperial']['Value'])))

            if temperature != windchill:
                output = string.replace(output, '{{windchill}}', '(Feels like %s&deg; with the wind)' % str(int(windchill)))
            else:
                output = string.replace(output, '{{windchill}}', '')

            output = string.replace(output, '{{cloudcover}}', str(self.data['CloudCover']))

            if precip > 0.0:
                output = string.replace(output, '{{precipitation}}', '<p>Precipitation in the past 24 hours: %s"</p>' % str(precip))
            else:
                output = string.replace(output, '{{precipitation}}', '')

        # These replacements hold true for all templates
        output = string.replace(output, '{{location}}', string.replace(self.location, '+', ' '))

        # Make sure the grammar on possesives ("Colorado Springs'") is correct.
        if self.location[-1] == 's':
            output = string.replace(output, '{{s}}', '')
        else:
            output = string.replace(output, '{{s}}', 's')

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
        

        ftp_path = '/DenverPost/weather/daily/'
        ftp_config = {
            'user': os.environ.get('FTP_USER'),
            'host': os.environ.get('FTP_HOST'),
            'port': os.environ.get('FTP_PORT'),
            'upload_dir': ftp_path
        }
        ftp = FtpWrapper(**ftp_config)
        ftp.send_file(path)
        ftp.disconnect()

        return "Successfully written to %s and FTP'd to %s" % ( path, ftp_path )

def main(args):
    wd = WeatherData(args)
    if args:
        for arg in args.locations[0]:
            if args.verbose:
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
            if args.verbose:
                print response

            # We also want to write a five-day version with the data:
            pub = PublishWeather(wd.response, '5day')
            pub.set_location(arg)
            pub.set_limit(4)
            pub.write_template()
            response = pub.write_file()
            if args.verbose:
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
            if args.verbose:
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
            if args.verbose:
                print response
            """

            log = LogWeather(wd.response)


if __name__ == '__main__':
    """ Takes a list of locations, passed as args.
        Example:
        $ python accuweather.py Denver Aspen "Grand Junction"
        """
    parser = argparse.ArgumentParser(usage='$ python accuweather.py Denver Aspen "Grand Junction"',
                                     description='Takes a list of locations passed as args.',
                                     epilog='')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("-c", "--cache", dest="cache", default=False, action="store_true")
    parser.add_argument("locations", action="append", nargs="*")
    args = parser.parse_args()

    if args.verbose:
        doctest.testmod(verbose=args.verbose)

    main(args)
