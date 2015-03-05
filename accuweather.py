#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Query the AccuWeather API
import os
import csv
from optparse import OptionParser

class WeatherData():
    def __init__(self):
        self.api_key = os.environ.get('API_KEY')
        self.api_url = os.environ.get('API_URL')
        if self.api_key == None or self.api_url == None:
            raise ValueError('Both API_KEY and API_URL environment variables must be set.')

if __name__ == 'main':
    pass
