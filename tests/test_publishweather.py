#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
import accuweather

def test_init():
    """ Test the class' init method.
        Note: This relies on env vars being set.
        """
    item = accuweather.PublishWeather('')
    assert item != None
