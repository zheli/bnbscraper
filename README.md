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
  * `superhos`
