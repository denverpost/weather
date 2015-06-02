#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Return recent items from a RSS feed.`
import os
import doctest
import json
import httplib2
import feedparser
import argparse
from datetime import date, timedelta

class RecentFeed:
    """ Methods for ingesting and publishing RSS feeds.
        """

    def __init__(self, args):
        self.args = args

    def get(self, url):
        """ Wrapper for API requests. Take a URL, return a json array.
            """
        h = httplib2.Http('.tmp')
        (response, content) = h.request(url, "GET")
        if response['status'] != '200':
            if self.options.verbose:
                print "URL: %s" % url
            raise ValueError("URL %s response: %s" % (url, response.status))
        return json.loads(content)

def main(args):
    rf = RecentFeed(args)
    if args:
        for arg in args.urls:
            if args.verbose:
                print arg


if __name__ == '__main__':
    """ 
        """
    parser = argparse.ArgumentParser(usage='$ python recentfeed.py http://domain.com/rss/',
                                     description='''Takes a list of URLs passed as args.
                                                  Returns the items published today unless otherwise specified.''',
                                     epilog='')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("-d", "--days", dest="days", default=0, action="count")
    parser.add_argument("urls", action="append", nargs="*")
    args = parser.parse_args()

    if args.verbose:
        doctest.testmod(verbose=args.verbose)

    main(args)
