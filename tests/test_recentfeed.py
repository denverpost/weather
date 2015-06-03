#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
import recentfeed

def test_init():
    """ Test the class' init method.
        """
    options = {}
    obj = recentfeed.RecentFeed(options)
    assert obj != None

def test_get():
    """ """
    options = {}
    obj = recentfeed.RecentFeed(options)
    #assert key == '347810'

def test_parse():
    """ """
    options = {}
    obj = recentfeed.RecentFeed(options)
    '''
    wd.set_location_key('Denver')
    request = {
        'type': 'forecasts',
        'slug': 'daily/10day/'
    }
    forecast = wd.get_from_api(request)
    assert forecast['Headline']['Link'] == 'http: //www.accuweather.com/en/us/denver-co/80203/daily-weather-forecast/347810?lang=en-us'
    '''
