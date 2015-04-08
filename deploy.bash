#!/bin/bash
# Update the weather data.
source source.bash
for CITY in `cat colorado-cities.txt`; do echo $CITY; python accuweather.py $CITY; done
