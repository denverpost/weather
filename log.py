#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Log the days we've written our nightly weather files.
import doctest
import argparse

def main(args):
    # Write the log file. 
    f = open('log_daily', 'wb')
    f.write(output)
    #f.close()

if __name__ == '__main__':
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    args = parser.parse_args()

    if args.verbose:
        doctest.testmod(verbose=args.verbose)

    main(args)
