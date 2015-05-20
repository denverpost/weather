#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Write our nightly weather files
import doctest
import argparse
from accuweather import WeatherData, PublishWeather

def main(args):
    wd = WeatherData(args)
    content = []
    if args:
        for arg in args.locations[0]:
            if args.verbose:
                print arg
            wd.set_location_key(arg)
            request = { 
                'type': 'currentconditions',
                'slug': '',
                'suffix': '&details=true'
            }
            wd.get_from_api(arg, **request)
            wd.write_cache(arg, **request)
            print wd.response

            output = self.template
            output = string.replace(output, '{{last24_high}}', str(int(self.data['TemperatureSummary']['Past24HourRange']['Maximum']['Imperial']['Value'])))
            output = string.replace(output, '{{last24_low}}', str(int(self.data['TemperatureSummary']['Past24HourRange']['Minimum']['Imperial']['Value'])))
            precip = self.data['PrecipitationSummary']['Past24Hours']['Imperial']['Value']
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
            self.slug = self.slug.replace('+', '_')
            path = 'www/output/%s-%s.html' % ( self.data_type, self.slug )
            f = open(path, 'wb')
            f.write(self.output)
            f.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='$ python nightly.py Denver Aspen "Grand Junction"',
                                     description='Takes a list of locations passed as args.',
                                     epilog='')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("-c", "--cache", dest="cache", default=False, action="store_true",
                        help="Pull from local cached data, make no external calls to Accuweather's API")
    parser.add_argument("locations", action="append", nargs="*")
    args = parser.parse_args()

    if args.verbose:
        doctest.testmod(verbose=args.verbose)

    main(args)
