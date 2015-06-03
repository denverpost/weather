#!/bin/bash
# Update the weather data.
source source.bash
DATE_SLUG=`date +'%F'`
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
    python recentfeed.py http://rss.denverpost.com/mngi/rss/CustomRssServlet/36/213601.xml > "www/output/headlines_"$DATE_SLUG".html"
    for CITY in `cat colorado-cities.txt`; do echo $CITY; python nightly.py $CITY; done
    RECORD=`python log.py`
    # Also build the indexes
    python nightly.py --indexes # This runs all the indexes
    #python nightly.py --index $RECORD
fi
