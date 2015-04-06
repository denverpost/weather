#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
import accuweather

def test_init():
    """ Test the class' init method.
        Note: This relies on env vars being set.
        """
    options = {}
    wd = accuweather.WeatherData(options)
    assert wd != None

def test_set_location_key():
    """ """
    options = {}
    wd = accuweather.WeatherData(options)
    key = wd.set_location_key('Denver')
    assert key == '347810'

def test_get_from_api():
    """ """
    options = {}
    wd = accuweather.WeatherData(options)
    wd.set_location_key('Denver')
    request = {
        'type': 'forecasts',
        'slug': 'daily/10day/'
    }
    forecast = wd.get_from_api(request)
    assert forecast['Headline']['Link'] == 'http: //www.accuweather.com/en/us/denver-co/80203/daily-weather-forecast/347810?lang=en-us'
