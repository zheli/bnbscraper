#!/bin/sh

cd /home/ubuntu/AirBnBScrapingProject/bnbscraper

QUERY="Rome--Italy"
FILTERS="neighborhood,property_type_id"
DATE="$(date +%F)"
LOGSEP="_"
LOGFILE="$DATE$LOGSEP$QUERY"
LOGFILE="$LOGFILE.log"
LOGFILE="/home/ubuntu/$LOGFILE"
OUTFILE="$QUERY.json"
OUTFILE="/home/ubuntu/$OUTFILE"
echo $OUTFILE
echo $LOGFILE
touch $OUTFILE
touch $LOGFILE
ls
scrapy crawl airbnb -a query=$QUERY -a filters=$FILTERS  -o $OUTFILE --loglevel INFO 2>&1 | tee $LOGFILE

