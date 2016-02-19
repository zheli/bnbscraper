import scrapy
from bnbscraper.bnbItem import BnbItem
import json


# TODO: implement the class to avoid calls to pages which are already crawled
# http://stackoverflow.com/questions/12553117/how-to-filter-duplicate-requests-based-on-url-in-scrapy

AIRBNB_URL = "https://www.airbnb.com/s/"

LISTING_ID_SEEN = set()

class AirbnbSpider(scrapy.Spider):
    """
    pass command line arguments as follows
    e.g. scrapy crawl airbnb -a query=Reggio-Emilia--Italy -o tests.json
    """
    def __init__(self, query=None, *args, **kwargs):
        super(AirbnbSpider, self).__init__(*args, **kwargs)
        self.start_urls = [AIRBNB_URL + query]


    name = "airbnb"
    allowed_domains = ["airbnb.com"]

    def parse(self, response):
        all_neighborhoods =  response.xpath('//input[@name="neighborhood"]/@value').extract()
        # test if there are any neighborhoods
        if not all_neighborhoods:
            # if not pass the first page to the parse result page
            yield scrapy.Request(self.start_urls[0], callback=lambda r, neigh=None: self.parse_start_page(r, neigh))
        else:
            for neighborhood in all_neighborhoods:
                neighborhood = neighborhood.replace(' ','+')
                request_url = self.start_urls[0]+'?'+'neighborhoods='+neighborhood
                yield scrapy.Request(request_url, callback=lambda r, neigh=neighborhood: self.parse_start_page(r, neigh))


    def parse_start_page(self, response, le_neighborhood):
        # this function is called to parse the individual links on the result page after any filter in the previous steps
        last_page_number = int(response
                               .xpath('//ul[@class="list-unstyled"]/li[last()-1]/a/@href')
                               .extract()[0]
                               .split('page=')[1]
                               )
        # use the request.url to add the right page not through simple cat
        if '?' in response.url:
            page_separator = '&'
        else:
            page_separator= '?'
        page_urls = [response.url + page_separator + "page=" + str(pageNumber)
                     for pageNumber
                     in range(1, last_page_number+1)
                     ]
        print '-----------------------------'
        print page_urls
        print '-----------------------------'
        # the function loops over all paginated result pages
        for page_url in page_urls:
            yield scrapy.Request(page_url, callback=lambda r, page=page_url, neigh=le_neighborhood: self.parse_listing_results_page(r, page, neigh))
            # send a request every time and set as callback the parseQueryPage



    def parse_listing_results_page(self, response, coming_from_page, le_neighborhood):
        for href in response.xpath('//div[@class="listing"]/@data-url').extract():
            url = response.urljoin(href)
            # yield scrapy.Request(url, callback=self.parse_dir_contents)

            yield scrapy.Request(url, callback=lambda r, page=coming_from_page, neigh=le_neighborhood:self.parse_dir_contents(r, page, neigh))

    def parse_dir_contents(self, response, coming_from_page, le_neighborhood):
        """
        This method extracts the actual data from the airbnb listing
        :param response: scrapy response object
        :return: item object
        """
        item = BnbItem()
        airbnb_json_all = json.loads(response.xpath('//meta[@id="_bootstrap-room_options"]/@content').extract()[0])
        airbnb_json = airbnb_json_all['airEventData']
        item['rev_count'] = airbnb_json['visible_review_count']
        item['amenities'] = airbnb_json['amenities']
        item['host_id'] = airbnb_json_all['hostId']
        item['hosting_id'] = airbnb_json['hosting_id']
        item['room_type'] = airbnb_json['room_type']
        item['price'] = airbnb_json['price']
        item['bed_type'] = airbnb_json['bed_type']
        item['person_capacity'] = airbnb_json['person_capacity']
        item['cancel_policy'] = airbnb_json['cancel_policy']
        item['rating_communication'] = airbnb_json['communication_rating']
        item['rating_cleanliness'] = airbnb_json['cleanliness_rating']
        item['rating_checkin'] = airbnb_json['checkin_rating']
        item['satisfaction_guest'] = airbnb_json['guest_satisfaction_overall']
        item['instant_book'] = airbnb_json['instant_book_possible']
        item['accuracy_rating'] = airbnb_json['accuracy_rating']
        item['response_time'] = airbnb_json['response_time_shown']
        item['response_rate'] = airbnb_json['reponse_rate_shown']
        item['url'] = response.url

        title = response.xpath('/html/head/meta[@property="og:title"]/@content').extract()
        if len(title):
            item['title'] = title[0]

        location = response.xpath('/html/head/meta[@property="airbedandbreakfast:locality"]/@content').extract()
        if len(location):
            item['location'] = location[0]

        region = response.xpath('/html/head/meta[@property="airbedandbreakfast:region"]/@content').extract()
        if len(region):
            item['region'] = region[0]

        country = response.xpath('/html/head/meta[@property="airbedandbreakfast:country"]/@content').extract()
        if len(country):
            item['country'] = country[0]

        lat = response.xpath(
            '/html/head/meta[@property="airbedandbreakfast:location:latitude"]/@content').extract()
        if len(lat):
            item['lat'] = float(lat[0])

        lng = response.xpath(
            '/html/head/meta[@property="airbedandbreakfast:location:longitude"]/@content').extract()
        if len(lng):
            item['lng'] = float(lng[0])

        bathrooms = response.xpath('//strong[contains(@data-reactid,"Bathrooms")]/text()').extract()
        if len(bathrooms):
            item['bathrooms'] = float(bathrooms[0])

        bedrooms = response.xpath('//strong[contains(@data-reactid,"Bedrooms")]/text()').extract()
        if len(bedrooms):
            item['bedrooms'] = float(bedrooms[0])


        beds = response.xpath('//strong[contains(@data-reactid,"Beds")]/text()').extract()
        if len(beds):
            item['beds'] = float(beds[0])

        propertyType = response.xpath('//strong[contains(@data-reactid,"Property type")]/text()').extract()
        if len(propertyType):
            item['propertyType'] = propertyType[0]

        extraPeople = response.xpath('//strong[contains(@data-reactid,"Extra people")]/text()').extract()
        if len(extraPeople):
            item['extraPeople'] = extraPeople[0]

        cleaningFee = response.xpath('//strong[contains(@data-reactid,"Cleaning")]/text()').extract()
        if len(cleaningFee):
            item['cleaningFee'] = cleaningFee[0]

        item['pageNumber'] = coming_from_page
        item['neighborhood'] = le_neighborhood

        yield item
