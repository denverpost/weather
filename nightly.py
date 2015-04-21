#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Write our nightly weather files
import doctest
import argparse
from accuweather import WeatherData, PublishWeather

def main(args):
    wd = WeatherData(args)
    if args:
        for arg in args.locations[0]:
            if args.verbose:
                print arg
            wd.set_location_key(arg)



if __name__ == '__main__':
    """ Takes a list of locations, passed as args.
        Example:
        $ python nightly.py Denver Aspen "Grand Junction"
        """
    parser = argparse.ArgumentParser(usage='', description='',
                                     epilog='')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("-c", "--cache", dest="cache", default=False, action="store_true")
    parser.add_argument("locations", action="append", nargs="*")
    args = parser.parse_args()

    if args.verbose:
        doctest.testmod(verbose=args.verbose)

    main(args)
