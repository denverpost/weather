#!/bin/bash
# Update the weather data.
source source.bash
NIGHTLY=0
while [ "$1" != "" ]; do
    case $1 in
        -n | --nightly) shift
            NIGHTLY=1
            ;;
    esac
    shift
done

if [ "$NIGHTLY" -eq 0 ]; then
    for CITY in `cat colorado-cities.txt`; do echo $CITY; python accuweather.py $CITY; done
else
    for CITY in `cat colorado-cities.txt`; do echo $CITY; python nightly.py $CITY; done
    python log.py
    # Also build the indexes
    python nightly.py --indexes
fi
