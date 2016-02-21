#!/bin/sh

cd $1

QUERY=$2
FILTERS="neighborhood,property_type_id,cancel_policies"
DATE="$(date +%F)"
SEP="_"
LOGFILE="$QUERY$SEP$DATE"
LOGFILE="$LOGFILE.log"
LOGFILE="./log/$LOGFILE"
OUTFILE="$QUERY$SEP$DATE.json"
OUTFILE="./scrapedQueries/$OUTFILE"
mkdir ./log/
mkdir ./scrapedQueries/
touch ${OUTFILE}
touch ${LOGFILE}
ls
# scrapy crawl airbnb -a query=${QUERY} -a filters=${FILTERS}  -o ${OUTFILE} | tee ${LOGFILE}

