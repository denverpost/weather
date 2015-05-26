#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Write our nightly weather files
import doctest
import argparse
import string
import os
from datetime import date
from accuweather import WeatherData, PublishWeather
from FtpWrapper import FtpWrapper

def main(args):
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
            output = string.replace(output, '{{url}}', url)

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




if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='$ python nightly.py Denver Aspen "Grand Junction"',
                                     description='Takes a list of locations passed as args.',
                                     epilog='')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("locations", action="append", nargs="*")
    args = parser.parse_args()

    if args.verbose:
        doctest.testmod(verbose=args.verbose)

    main(args)
