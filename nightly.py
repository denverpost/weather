#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Write our nightly weather files
import argparse
import string
import os, sys
from FtpWrapper import FtpWrapper
import csv
from datetime import date, datetime
try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict
from accuweather import WeatherData, PublishWeather
from weatherutils import WeatherCsv, WeatherLog


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
        'breadcrumb_one': '',
        'breadcrumb_two': '',
        'breadcrumb_three': '',
        'description': 'Weather temperatures and rainfall data for each of Colorado\'s cities and towns.'
    }
    log = WeatherLog('index', **metadata)
    content = log.parse_template()
    path = log.write_html(content, '')
    ftp_path = '/DenverPost/weather/historical/'
    log.ftp_page(path, ftp_path)

    # Allow us to specify the locations via args, or else just run it on all the cities.
    if 'locations' in args and len(args.locations[0]) > 0:
        locations = args.locations[0]
    else:
        f = open('colorado-cities.txt', 'rb')
        content = f.read()
        f.close()
        locations = content.split('\n')

    for location in locations:
        if location == '':
            continue

        # Make sure the grammar on possesives ("Colorado Springs'") is correct.
        s = ''
        if location[-1] == 's':
            s = ''
        else:
            s = 's'

        #++++++++++++++++++++++++++++++++++++++++
        # City Weather Index
        #++++++++++++++++++++++++++++++++++++++++
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
            'breadcrumb_one': '',
            'breadcrumb_two': '',
            'breadcrumb_three': '',
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
        day_dict = OrderedDict()
        for date in dates:
            d = dict(zip(date_header, date.split(',')))
            # returns {'date': '27', 'path': '2015/may/27', 'month': 'may', 'year': '2015'}
            if d['year'] == '':
                continue

            # Check if the year exists in our dict
            if d['year'] not in day_dict:
                day_dict[d['year']] = OrderedDict()

            if d['month'] not in day_dict[d['year']]:
                day_dict[d['year']][d['month']] = OrderedDict()

            # Each date's only in the dict once, this we know.
            day_dict[d['year']][d['month']][d['date']] = d['path']

        #++++++++++++++++++++++++++++++++++++++++
        # Year Weather Index
        #++++++++++++++++++++++++++++++++++++++++
        for year in day_dict:
            metadata = {
                's': s,
                'year': year,
                'months': day_dict[year],
                'month': '{{month}}',
                'days': '',
                'location': location,
                'url': 'http://extras.denverpost.com/weather/historical/%s/%s/' % (slug, year),
                'title': 'Weather in %s, in %s, Colorado' % (year, location_display),
                'breadcrumb_one': '&rsaquo; <a href="../">%s</a>' % location_display,
                'breadcrumb_two': '',
                'breadcrumb_three': '',
                'description': '%s temperatures and rainfall data for %s, Colorado.' % (year, location_display)
            }
            log = WeatherLog('index_year', **metadata)
            content = log.parse_template()
            path = log.write_html(content, 'index')
            ftp_path = '/DenverPost/weather/historical/%s/%s/' % (slug, year)
            log.ftp_page(path, ftp_path)

            #++++++++++++++++++++++++++++++++++++++++
            # Month Weather Index
            #++++++++++++++++++++++++++++++++++++++++
            for month in day_dict[year]:
                metadata = {
                    's': s,
                    'year': year,
                    'months': '',
                    'month': month,
                    'days': day_dict[year][month],
                    'location': location,
                    'url': 'http://extras.denverpost.com/weather/historical/%s/%s/%s/' % (slug, year, month),
                    'title': '%s %s historic weather in %s, Colorado' % (month.title(), year, location_display),
                    'breadcrumb_one': '&rsaquo; <a href="../../">%s</a>' % location_display,
                    'breadcrumb_two': '&rsaquo; <a href="../">%s</a>' % year,
                    'breadcrumb_three': '',
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

        #++++++++++++++++++++++++++++++++++++++++
        # Daily Weather 
        #++++++++++++++++++++++++++++++++++++++++
        
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
            request = {
                'type': 'climo',
                'slug': '/records/2015/06/',
                'suffix': ''
            }
            wd.get_from_api(location, **request)
            climo_data = wd.response
            print climo_data
            sys.exit()
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
            try:
                f = open('www/output/headlines_%s.html' % date_slug)
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
            output = string.replace(output, '{{breadcrumb_one}}', '&rsaquo; <a href="../../../">%s</a>' % location)
            output = string.replace(output, '{{breadcrumb_two}}', '&rsaquo; <a href="../../">%d</a>' % date.today().year)
            output = string.replace(output, '{{breadcrumb_three}}', '&rsaquo; <a href="../">%s</a>' % date.strftime(date.today(), '%B'))
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
