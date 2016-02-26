# This is a scrapy project to scrape some basic info from AirBnB


## Usage

```bash
scrapy crawl airbnb -a query=<CITY> -a filter=<FILTER1,FILTER2> -o tests.json
```

the filters are supplied as `-a filter=<FILTER1,FILTER2>` they must be comma separatedpossible values for the filters are:
 
  * `amenities`
  * `checkin`
  * `checkout`
  * `instant_book`
  * `languages`
  * `location`
  * `neighborhood`
  * `property_type_id`
  * `room-type`
  * `source`
  * `superhost`

Advanced usage:
```bash
>> scrapy crawl airbnb -a query=Rome--Italy -a filters=neighborhood,property_type_id -o output.json  2>&1 | tee ~/<log>.log
```


To use the script with some default shell parameters, simply pass as first argument the city as query:
```bash
>> ./runSearch.sh <workingDir> Rome--Italy
```

db.listings.aggregate([
                      {$group: {_id: '$hosting_id',
                                count: {$sum: 1}
                               }
                      },
                      {$match: {count: {$gt:1} } }
                     ])