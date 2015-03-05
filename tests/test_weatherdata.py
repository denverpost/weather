#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
import accuweather

def test_init():
    """ Test the class' init method.
        Note: This relies on env vars being set.
        """
    wd = accuweather.WeatherData()
    assert weatherdata != None

def test_set_location_key():
    """ """
    wd = accuweather.WeatherData()
    key = wd.set_location_key('Denver')
    assert key == '347810'

def test_get_forecast():
    """ """
    wd = accuweather.WeatherData()
    wd.set_location_key('Denver')
    forecast = wd.get_forecast('10day')
    assert forecast['Headline']['Link'] == 'http: //www.accuweather.com/en/us/denver-co/80203/daily-weather-forecast/347810?lang=en-us'
