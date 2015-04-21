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
            print wd.respose



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
