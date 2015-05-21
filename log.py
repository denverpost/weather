#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Log the days we've written our nightly weather files.
import doctest
import argparse
from datetime import date

def main(args):
    path_vars = {
        'year': date.today().year,
        'month': date.strftime(date.today(), '%B').lower(),
        'day': date.today().day
    }
    url = '%(year)s/%(month)s/%(day)s' % path_vars
    day = date.strftime(date.today(), '%Y,%B,%-m')
    record = "%s,%s" % (day,url)

    # Write the log file. 
    f = open('log_daily.csv', 'wb')
    f.write(output)
    f.close()

if __name__ == '__main__':
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    args = parser.parse_args()

    if args.verbose:
        doctest.testmod(verbose=args.verbose)

    main(args)
