#!/bin/sh

cd /home/ubuntu/AirBnBScrapingProject/bnbscraper

QUERY=$1
FILTERS="neighborhood,property_type_id"
DATE="$(date +%F)"
LOGSEP="_"
LOGFILE="$QUERY$LOGSEP$DATE"
LOGFILE="$LOGFILE.log"
LOGFILE="./$LOGFILE"
OUTFILE="$QUERY$LOGSEP$DATE.json"
OUTFILE="./$OUTFILE"
echo $OUTFILE
echo $LOGFILE
touch $OUTFILE
touch $LOGFILE
ls
scrapy crawl airbnb -a query=$QUERY -a filters=$FILTERS  -o $OUTFILE --loglevel INFO | tee $LOGFILE

