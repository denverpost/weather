#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Log the days we've written our nightly weather files.
import doctest
import argparse
import pickle
from datetime import date

def main(args):
    path_vars = {
        'year': date.today().year,
        'month': date.strftime(date.today(), '%B').lower(),
        'day': date.today().day
    }
    url = '%(year)s/%(month)s/%(day)s' % path_vars
    path_vars['path'] = url
    day = date.strftime(date.today(), '%Y,%B,%d').lower()
    record = "%s,%s\n" % (day,url)

    # Write the log file. 
    f = open('log_daily.csv', 'ab')
    f.write(record)
    f.close()
    print pickle.dumps(path_vars)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='$ python log.py',
                                     description='Add an entry to a CSV of days we have logged the weather',
                                     epilog='')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    args = parser.parse_args()

    if args.verbose:
        doctest.testmod(verbose=args.verbose)

    main(args)
