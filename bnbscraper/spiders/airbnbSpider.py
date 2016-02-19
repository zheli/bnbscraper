import scrapy
from bnbscraper.bnbItem import BnbItem
import json

AIRBNB_URL = "https://www.airbnb.com/s/"



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
        # TODO: implement the following construct
        # - navigate to the start_urls and obtain the neighboorhoods
        #   using response.xpath('//input[@name="neighborhood"]/@value').extract()
        # - concatenate as necessary and go to new search page and pass to new parse function
        # - obtain last_page number from this query page and implement as below




        # this function is called the first time to get the first page and see how many links there are
        last_page_number = int(response
                               .xpath('//ul[@class="list-unstyled"]/li[last()-1]/a/@href')
                               .extract()[0]
                               .split('page=')[1]
                               )
        page_urls = [self.start_urls[0] + "?&page=" + str(pageNumber)
                     for pageNumber
                     in range(2, 3)
                     ]
        page_urls = self.start_urls + page_urls

        # the function loops over all paginated result pages
        for page_url in page_urls:
            yield scrapy.Request(page_url, callback=lambda r, page=page_url: self.parse_query_page(r, page))
            # send a request every time and set as callback the parseQueryPage

    def parse_query_page(self, response, fromPage):
        for href in response.xpath('//div[@class="listing"]/@data-url').extract():
            url = response.urljoin(href)
            # yield scrapy.Request(url, callback=self.parse_dir_contents)

            yield scrapy.Request(url, callback=lambda r, page=fromPage:self.parse_dir_contents(r, page))

    def parse_dir_contents(self, response, fromPage):
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

        item['pageNumber'] = fromPage

        yield item
