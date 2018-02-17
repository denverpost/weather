#!/usr/bin/python
# -*- coding: utf-8 -*-
# Write our nightly weather files
import doctest
import string
import os
import csv
from FtpWrapper import FtpWrapper

class WeatherCsv():
    """ Query the log_daily.csv file:
            1. Get a list of months per year.
            2. Get a list of days per month.
            3. Get a list of years.
        >>> wc = WeatherCsv('log_daily.test.csv')
        >>> years = wc.get_years()
        >>> print years[0]
        2015
        >>> months = wc.get_months(years[0])
        >>> print months[0]
        january
        >>> dates = wc.get_dates(years[0], months[0])
        >>> print dates[0]
        01
        """

    def __init__(self, fn):
        try:
            f = open(fn, 'rb')
        except:
            f = open('log_daily.csv', 'rb')

        dates = f.read().split('\n')
        f.close()
        self.date_header = dates[0].split(',')
        self.dates = dates[1:]

    def get_years(self):
        """ Return a list of unique years.
            """
        years = []
        for date in self.dates:
            d = dict(zip(self.date_header, date.split(',')))
            # returns {'date': '27', 'path': '2015/may/27', 'month': 'may', 'year': '2015'}
            if d['year'] == '':
                continue
            years.append(d['year'])
        return list(set(years))

    def get_months(self, year):
        """ Return a list of unique months for a particular year.
            """
        months = []
        for date in self.dates:
            d = dict(zip(self.date_header, date.split(',')))
            # returns {'date': '27', 'path': '2015/may/27', 'month': 'may', 'year': '2015'}
            if d['year'] != year:
                continue
            months.append(d['month'])
        return list(set(months))

    def get_dates(self, year, month):
        """ Return a list of unique dates for a particular year/month.
            """
        dates = []
        for date in self.dates:
            d = dict(zip(self.date_header, date.split(',')))
            # returns {'date': '27', 'path': '2015/may/27', 'month': 'may', 'year': '2015'}
            if d['year'] != year or d['month'] != month:
                continue
            dates.append(d['date'])
        return list(set(dates))


class WeatherLog():
    """ Publish flat files based on csv logs of data."""

    def __init__(self, data_type, **metadata):
        """
            """
        self.data_type = data_type
        self.metadata = metadata
        self.locations = self.read_file('colorado-cities.txt').split('\n')
        if self.metadata['location'] != '':
            self.slug = string.replace(self.metadata['location'], ' ', '_').lower()

    def read_file(self, fn):
        """ Read the contents of a file.
            """
        f = open(fn, 'rb')
        content = f.read()
        f.close()
        return content

    def build_content(self, template):
        """ Put together the content we're writing to the page.
            This method takes the markup in the row template and stores it
            in a var named item, which is appended to a list named content,
            which is returned in one giant text blob at the end of the method.
            """
        if template == '':
            template = self.data_type

        fn = 'html/%s.row.html' % template
        item_tmp = self.read_file(fn)
        
        content = []

        if self.data_type == 'index':
            for location in self.locations:
                item = string.replace(item_tmp, '{{location}}', string.replace(location, '+', ' '))
                item = string.replace(item, '{{url}}', string.replace(location, '+', '_').lower())
                content.append(item)
        elif self.data_type in ['index_city', 'index_year', 'index_month']:
            item = string.replace(item_tmp, '{{location}}', string.replace(self.metadata['location'], '+', ' '))
            item = string.replace(item, '{{url}}', '2017')
            item = string.replace(item, '{{year}}', self.metadata['year'])
            item = string.replace(item, '{{month}}', self.metadata['month'].title())
            item = string.replace(item, '{{s}}', self.metadata['s'])
            item = string.replace(item, '{{slug}}', string.replace(self.slug, '+', '_'))


            if self.data_type == 'index_city':
                wc = WeatherCsv('log_daily.csv')
                years = wc.get_years()
                months_list = wc.get_months(years[0])
                months = []
                for month in months_list:
                    months.append('<a href="%s/%s/">%s</a>' % (years[0], month, month.title()))
                months_blurb = " ".join(months)
                item = string.replace(item, '{{months}}', months_blurb)

            # Some fields are dicts. 
            # They're dicts because they're meant to be looped through.
            # They're meant to be looped through to give people a list of the available data.
            if self.metadata['months'] != '':
                item_original = item
                for month, days in self.metadata['months'].iteritems():
                    print month
                    item = string.replace(item_original, '{{path}}', month)
                    item = string.replace(item, '{{Month}}', month.title())
                    content.append(item)
            elif self.metadata['days'] != '':
                item_original = item
                for day, path in iter(sorted(self.metadata['days'].iteritems())):
                    item = string.replace(item_original, '{{day}}', day)
                    item = string.replace(item, '{{path}}', path)
                    content.append(item)
            else:
                content.append(item)

        return "\n".join(content)

    def parse_template(self):
        """ Take the content put together in build_content() and put it in 
            the content wrapper (which is then put in the page wrapper).
            """
        template = self.data_type

        fn = 'html/%s.html' % template
        template = self.read_file(fn)
        content = self.build_content('')
        template = string.replace(template, '{{content}}', content)

        page = self.read_file('html/page.html')
        template = string.replace(page, '{{content}}', template)
        template = string.replace(template, '{{location}}', string.replace(self.metadata['location'], '+', ' '))
        template = string.replace(template, '{{url}}', string.replace(self.metadata['url'], '+', '_'))
        template = string.replace(template, '{{title}}', self.metadata['title'])
        template = string.replace(template, '{{description}}', self.metadata['description'])
        template = string.replace(template, '{{year}}', self.metadata['year'])
        template = string.replace(template, '{{month}}', self.metadata['month'].title())
        template = string.replace(template, '{{s}}', self.metadata['s'])
        template = string.replace(template, '{{breadcrumb_one}}', self.metadata['breadcrumb_one'])
        template = string.replace(template, '{{breadcrumb_two}}', self.metadata['breadcrumb_two'])
        template = string.replace(template, '{{breadcrumb_three}}', self.metadata['breadcrumb_three'])
        if self.metadata['location'] != '':
            template = string.replace(template, '{{slug}}', self.slug)
        return template

    def write_html(self, output, fn):
        """ Take the markup and put it in a file.
            """
        if fn == '':
            fn = self.data_type
        path = 'www/output/%s.html' % fn
        f = open(path, 'wb')
        f.write(output)
        f.close()
        return path

    def ftp_page(self, file_path, ftp_path):
        """ Take the file and FTP it to prod.
            """
        ftp_config = {
            'user': os.environ.get('FTP_USER'),
            'host': os.environ.get('FTP_HOST'),
            'port': os.environ.get('FTP_PORT'),
            'upload_dir': ftp_path
        }
        ftp = FtpWrapper(**ftp_config)
        ftp.mkdir()
        ftp.send_file(file_path)
        ftp.disconnect()
