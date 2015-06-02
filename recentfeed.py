#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Return recent items from a RSS feed. Recent means "In the last X days."
import os
import doctest
import json
import httplib2
import feedparser
import argparse
from datetime import datetime, timedelta
from time import mktime

class RecentFeed:
    """ Methods for ingesting and publishing RSS feeds.
        """

    def __init__(self, args):
        self.args = args

    def get(self, url):
        """ Wrapper for API requests. Take a URL, return a json array.
            >>> http://rss.denverpost.com/mngi/rss/CustomRssServlet/36/213601.xml
            """
        h = httplib2.Http('.tmp')
        (response, xml) = h.request(url, "GET")
        if response['status'] != '200':
            if self.args.verbose:
                print "URL: %s" % url
            raise ValueError("URL %s response: %s" % (url, response.status))
        self.xml = xml
        return xml

    def parse(self, xml):
        """ Turn the xml into an object.
            """
        if xml == '':
            xml = self.xml
        p = feedparser.parse(xml)
        self.p = p
        return p

    def recently(self):
        """ Return a json representation of the last X days of feed items.
            """
        items = []
        for item in self.p.entries:
            dt = datetime.fromtimestamp(mktime(item.published_parsed))
            delta = datetime.today() - dt

            if delta.days > self.args.days:
                continue
            items.append(item)
            if self.args.verbose:
                print delta.days, dt
        self.items = items
        return items

def main(args):
    rf = RecentFeed(args)
    if args:
        articles = []
        for arg in args.urls[0]:
            if args.verbose:
                print arg
            rf.get(arg)
            rf.parse('')
            articles.append(rf.recently())


        for article in articles:
            pass


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
