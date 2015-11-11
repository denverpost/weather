#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
from weatherutils import WeatherCsv

def test_init():
    """ Test the class' init method.
        """
    item = WeatherLog()
    assert item != None
