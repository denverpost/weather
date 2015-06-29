#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Write our nightly weather files
import doctest
import argparse
import string
import os
import csv
from datetime import date, datetime
from accuweather import WeatherData, PublishWeather
from FtpWrapper import FtpWrapper

class WeatherCsv():
    """ Query the log_daily.csv file:
            1. Get a list of months per year.
            2. Get a list of days per month.
            3. Get a list of years.
        """

    def __init__(self):
        f = open('log_daily.csv', 'rb')
        dates = f.read().split('\n')
        f.close()
        self.date_header = dates[0].split(',')
        self.dates = dates[1:]

    def get_years(self):
        """ Return a set of years.
            """
        years = []
        for date in self.dates:
            d = dict(zip(self.date_header, date.split(',')))
            # returns {'date': '27', 'path': '2015/may/27', 'month': 'may', 'year': '2015'}
            if d['year'] == '':
                continue
            years.append(d['year'])
        return set(years)

    def get_months(self, year):
        """ Return a set of months for a particular year.
            """
        months = []
        for date in self.dates:
            d = dict(zip(self.date_header, date.split(',')))
            # returns {'date': '27', 'path': '2015/may/27', 'month': 'may', 'year': '2015'}
            if d['year'] != year:
                continue
            months.append(d['month'])
        return set(months)

    def get_days(self, year, month):
        """ Return a set of days for a particular year/month.
            """
        days = []
        for date in self.dates:
            d = dict(zip(self.date_header, date.split(',')))
            # returns {'date': '27', 'path': '2015/may/27', 'month': 'may', 'year': '2015'}
            if d['year'] != year or d['month'] != month:
                continue
            days.append(d['date'])
        return set(days)

class WeatherLog():
    """ Publish flat files based on csv logs of data."""

    def __init__(self, data_type, **metadata):
        """
            """
        self.data_type = data_type
        self.metadata = metadata
        self.locations = self.read_file('colorado-cities.txt').split('\n')
        if self.metadata['location'] != '':
            self.slug = string.replace(self.metadata['location'], ' ', '_').lower()

    def read_file(self, fn):
        """
            """
        f = open(fn, 'rb')
        content = f.read()
        f.close()
        return content

    def build_content(self, template):
        """ Put together the content we're writing to the page.
            """
        if template == '':
            template = self.data_type

        fn = 'html/%s.row.html' % template
        template = self.read_file(fn)
        
        content = []

        if self.data_type == 'index':
            for location in self.locations:
                item = string.replace(template, '{{location}}', string.replace(location, '+', ' '))
                item = string.replace(item, '{{url}}', string.replace(location, '+', '_').lower())
                content.append(item)
        elif self.data_type in ['index_city', 'index_year', 'index_month']:
            item = string.replace(template, '{{location}}', string.replace(self.metadata['location'], '+', ' '))
            item = string.replace(item, '{{url}}', '2015')
            item = string.replace(item, '{{year}}', self.metadata['year'])
            item = string.replace(item, '{{month}}', self.metadata['month'].title())
            item = string.replace(item, '{{s}}', self.metadata['s'])
            item = string.replace(item, '{{slug}}', string.replace(self.slug, '+', '_'))

            # Some fields are dicts. 
            # They're dicts because they're meant to be looped through.
            # They're meant to be looped through to give people a list of the available data.
            if self.metadata['months'] != '':
                item_original = item
                for month, days in self.metadata['months'].iteritems():
                    item = string.replace(item_original, '{{path}}', month)
                    item = string.replace(item, '{{Month}}', month.title())
                    content.append(item)
            elif self.metadata['days'] != '':
                item_original = item
                for day, path in iter(sorted(self.metadata['days'].iteritems())):
                    item = string.replace(item_original, '{{day}}', day)
                    item = string.replace(item, '{{path}}', path)
                    content.append(item)
            else:
                content.append(item)

        return "\n".join(content)

    def parse_template(self):
        """ Take the content put together in build_content() and put it in 
            the content wrapper (which is then put in the page wrapper).
            """
        template = self.data_type

        fn = 'html/%s.html' % template
        template = self.read_file(fn)
        content = self.build_content('')
        template = string.replace(template, '{{content}}', content)

        page = self.read_file('html/page.html')
        template = string.replace(page, '{{content}}', template)
        template = string.replace(template, '{{location}}', string.replace(self.metadata['location'], '+', ' '))
        template = string.replace(template, '{{url}}', string.replace(self.metadata['url'], '+', '_'))
        template = string.replace(template, '{{title}}', self.metadata['title'])
        template = string.replace(template, '{{description}}', self.metadata['description'])
        template = string.replace(template, '{{year}}', self.metadata['year'])
        template = string.replace(template, '{{month}}', self.metadata['month'].title())
        template = string.replace(template, '{{s}}', self.metadata['s'])
        if self.metadata['location'] != '':
            template = string.replace(template, '{{slug}}', self.slug)
        return template

    def write_html(self, output, fn):
        """ Take the markup and put it in a file.
            """
        if fn == '':
            fn = self.data_type
        path = 'www/output/%s.html' % fn
        f = open(path, 'wb')
        f.write(output)
        f.close()
        return path

    def ftp_page(self, file_path, ftp_path):
        """ Take the file and FTP it to prod.
            """
        ftp_config = {
            'user': os.environ.get('FTP_USER'),
            'host': os.environ.get('FTP_HOST'),
            'port': os.environ.get('FTP_PORT'),
            'upload_dir': ftp_path
        }
        ftp = FtpWrapper(**ftp_config)
        ftp.mkdir()
        ftp.send_file(file_path)
        ftp.disconnect()

def indexes(args):
    """ Build the indexes for everything leading up to the daily page views.
        """
    metadata = {
        's': '',
        'year': '',
        'months': '',
        'month': '',
        'days': '',
        'location': '',
        'url': 'http://extras.denverpost.com/weather/historical/',
        'title': 'Colorado\'s Historical Weather Data',
        'breadcrumbs': '',
        'description': 'Weather temperatures and rainfall data for each of Colorado\'s cities and towns.'
    }
    log = WeatherLog('index', **metadata)
    content = log.parse_template()
    path = log.write_html(content, '')
    ftp_path = '/DenverPost/weather/historical/'
    log.ftp_page(path, ftp_path)

    f = open('colorado-cities.txt', 'rb')
    content = f.read()
    f.close()
    for location in content.split('\n'):
        if location == '':
            continue

        # Make sure the grammar on possesives ("Colorado Springs'") is correct.
        s = ''
        if location[-1] == 's':
            s = ''
        else:
            s = 's'

        slug = string.replace(location, '+', '_').lower()
        location_display = string.replace(location, '+', ' ')
        metadata = {
            's': s,
            'year': '2015',
            'months': '',
            'month': '',
            'days': '',
            'location': location,
            'url': 'http://extras.denverpost.com/weather/historical/%s/' % slug,
            'title': '%s, Colorado: Historical Weather' % location_display,
            'breadcrumbs': '',
            'description': '%s weather temperatures and rainfall data.' % location_display
        }
        log = WeatherLog('index_city', **metadata)
        content = log.parse_template()
        path = log.write_html(content, 'index')
        ftp_path = '/DenverPost/weather/historical/%s/' % slug
        log.ftp_page(path, ftp_path)


        # Now we write the year and month indexes
        f = open('log_daily.csv', 'rb')
        dates = f.read().split('\n')
        f.close()
        date_header = dates[0].split(',')
        dates = dates[1:]
        current_year = 0
        current_month = ''
        current_days = []

        # We need the distinct months and years from the dates.
        # We also need the indvidual dates for each month.
        day_dict = {}
        for date in dates:
            d = dict(zip(date_header, date.split(',')))
            # returns {'date': '27', 'path': '2015/may/27', 'month': 'may', 'year': '2015'}
            if d['year'] == '':
                continue

            # Check if the year exists in our dict
            if d['year'] not in day_dict:
                day_dict[d['year']] = {}

            if d['month'] not in day_dict[d['year']]:
                day_dict[d['year']][d['month']] = {}

            # Each date's only in the dict once, this we know.
            day_dict[d['year']][d['month']][d['date']] = d['path']

        for year in day_dict:
            # YEAR
            metadata = {
                's': s,
                'year': year,
                'months': day_dict[year],
                'month': '{{month}}',
                'days': '',
                'location': location,
                'url': 'http://extras.denverpost.com/weather/historical/%s/%s/' % (slug, year),
                'title': 'Weather in %s, in %s, Colorado' % (year, location_display),
                'breadcrumbs': '',
                'description': '%s temperatures and rainfall data for %s, Colorado.' % (year, location_display)
            }
            log = WeatherLog('index_year', **metadata)
            content = log.parse_template()
            path = log.write_html(content, 'index')
            ftp_path = '/DenverPost/weather/historical/%s/%s/' % (slug, year)
            log.ftp_page(path, ftp_path)

            for month in day_dict[year]:
                # MONTH
                metadata = {
                    's': s,
                    'year': year,
                    'months': '',
                    'month': month,
                    'days': day_dict[year][month],
                    'location': location,
                    'url': 'http://extras.denverpost.com/weather/historical/%s/%s/%s/' % (slug, year, month),
                    'title': '%s %s weather in %s, Colorado' % (month.title(), year, location_display),
                    'breadcrumbs': '',
                    'description': '%s %s temperatures and rainfall data for %s, Colorado.' % (month.title(), year, location_display)
                }
                log = WeatherLog('index_month', **metadata)
                content = log.parse_template()
                path = log.write_html(content, 'index')
                ftp_path = '/DenverPost/weather/historical/%s/%s/%s/' % (slug, year, month)
                log.ftp_page(path, ftp_path)

                for day, path in day_dict[year][month].iteritems():
                    print year, month, day, path
            

def main(args):
    """ Write the the-weather-on-this-day page, upload it.
        """
    wd = WeatherData(args)
    content = []
    if args:
        for location in args.locations[0]:
            if args.verbose:
                print location
            wd.set_location_key(location)
            request = { 
                'type': 'currentconditions',
                'slug': '',
                'suffix': '&details=true'
            }
            wd.get_from_api(location, **request)
            wd.write_cache(location, **request)
            data = wd.response[0]
            slug = string.lower(string.replace(location, ' ', '_'))
            slug = string.lower(string.replace(slug, '+', '_'))

            """
            # RETURNS 403's rn
            request = {
                'type': 'climo',
                'slug': '/records/2015/06/',
                'suffix': ''
            }
            wd.get_from_api(location, **request)
            climo_data = wd.response[0]
            """

            data_type = 'dailyconditions'
            path = 'html/%s.html' % data_type
            f = open(path, 'rb')
            template = f.read()
            f.close()

            output = template
            output = string.replace(output, '{{last24_high}}', str(int(data['TemperatureSummary']['Past24HourRange']['Maximum']['Imperial']['Value'])))
            output = string.replace(output, '{{last24_low}}', str(int(data['TemperatureSummary']['Past24HourRange']['Minimum']['Imperial']['Value'])))
            precip = data['PrecipitationSummary']['Past24Hours']['Imperial']['Value']
            if precip > 0.0:
                output = string.replace(output, '{{precipitation}}', '<p>Precipitation on this day: %s"</p>' % str(precip))
            else:
                output = string.replace(output, '{{precipitation}}', '<p>There was no precipitation on this day.</p>')


            # Get the weather news headlines
            date_slug = datetime.strftime(date.today(), "%Y-%m-%d")
            f = open('www/output/headlines_%s.html' % date_slug)
            try:
                weathernews = f.read()
            except:
                weathernews = ''
            f.close()
            if weathernews == '':
                weathernews = '<p>Nope, no <a href="http://www.denverpost.com/weathernews">weather news in Colorado</a> today.</p>'
            else:
                weathernews = '<ul>%s</ul>' % weathernews
            output = string.replace(output, '{{weathernews}}', weathernews)

            
            # Make sure the grammar on possesives ("Colorado Springs'") is correct.
            s = ''
            if location[-1] == 's':
                output = string.replace(output, '{{s}}', '')
            else:
                s = 's'
                output = string.replace(output, '{{s}}', 's')


            # Stick this into the page wrapper.
            data_type = 'page'
            path = 'html/%s.html' % data_type
            f = open(path, 'rb')
            template = f.read()
            f.close()
            day = date.strftime(date.today(), '%B %-d, %Y')
            output = string.replace(template, '{{content}}', output)
            output = string.replace(output, '{{location}}', string.replace(location, '+', ' '))
            output = string.replace(output, '{{day}}', day)
            output = string.replace(output, '{{slug}}', slug)
            title = "%s'%s weather on %s" % (string.replace(location, '+', ' '), s, day)
            output = string.replace(output, '{{title}}', title)
            description = "Here's the historical weather data for %s on %s" % (location, day)
            output = string.replace(output, '{{description}}', description)
            path_vars = {
                'location': string.replace(slug, '+', '_'),
                'year': date.today().year,
                'month': date.strftime(date.today(), '%B').lower(),
                'day': date.today().day
            }
            url = 'http://extras.denverpost.com/weather/historical/%(location)s/%(year)s/%(month)s/%(day)s/daily-weather-%(location)s.html' % path_vars
            output = string.replace(output, '{{url}}', string.replace(url, '+', '_'))

            slug = slug.replace('+', '_')
            path = 'www/output/daily-weather-%s.html' % ( slug )
            f = open(path, 'wb')
            f.write(output)
            f.close()

            # Write the index file
            #f = open('www/output/historical-weather-index.html', 'wb')
            #f.write(output)
            #f.close()

            # FTP this.
            ftp_path = '/DenverPost/weather/historical/%(location)s/%(year)s/%(month)s/%(day)s/' % path_vars
            ftp_config = {
                'user': os.environ.get('FTP_USER'),
                'host': os.environ.get('FTP_HOST'),
                'port': os.environ.get('FTP_PORT'),
                'upload_dir': ftp_path
            }
            ftp = FtpWrapper(**ftp_config)
            ftp.mkdir()
            ftp.send_file(path)
            ftp.disconnect()


def build_parser():
    """ This method allows us to test. You gotta write tests for this Joe.
        """
    parser = argparse.ArgumentParser(usage='$ python nightly.py Denver Aspen Grand+Junction',
                                     description='Takes a list of locations passed as args.',
                                     epilog='')
    parser.add_argument("-i", "--indexes", dest="indexes", default=False, action="store_true")
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("locations", action="append", nargs="*")
    return parser

if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose:
        doctest.testmod(verbose=args.verbose)

    # The list pages: /denver/, /denver/2015/, /denver/2015/june/
    if args.indexes:
        indexes(args)
    else:
        # The detail page: /denver/2015/june/8/daily-weather-denver.html
        main(args)
