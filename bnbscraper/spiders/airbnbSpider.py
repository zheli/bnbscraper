import scrapy
from bnbscraper.bnbItem import BnbItem
import json
import urllib
import itertools


AIRBNB_URL = "https://www.airbnb.com/s/"


class AirbnbSpider(scrapy.Spider):
    """
    pass command line arguments as follows
    e.g. scrapy crawl airbnb -a query=Reggio-Emilia--Italy filters=neighborhood,propertytype-o tests.json
    """
    def __init__(self, query='', filters='', *args, **kwargs):
        super(AirbnbSpider, self).__init__(*args, **kwargs)
        self.start_urls = [AIRBNB_URL + query]
        self.bnb_filters = [filter.strip() for filter in list(filters.split(','))]

    name = "airbnb"
    allowed_domains = ["airbnb.com"]

    def parse(self, response):
        filter_dict =  self.extract_filter_property(response)
        # test if there are any neighborhoods
        if not filter_dict:
            # if not pass the first page to the parse result page
            yield scrapy.Request(self.start_urls[0], callback=self.parse_start_page)
        else:
            all_combinations = self.filter_dict_to_tuple(filter_dict)
            for filter_combination in self.filter_combinations_generator(all_combinations):
                # query_string = urllib.urlencode(filter_combination)
                query_string = '&'.join([k+'='+v for k, v in filter_combination])
                request_url = self.start_urls[0]+'?'+query_string

                yield scrapy.Request(request_url, callback=self.parse_start_page)


    def parse_start_page(self, response):
        # this function is called to parse the individual links on the result page after any filter in the previous steps

        try:
            last_page_number = int(response
                               .xpath('//ul[@class="list-unstyled"]/li[last()-1]/a/@href')
                               .extract()[0]
                               .split('page=')[1]
                               )
        except:
            last_page_number = 1

        # use the request.url to add the right page not through simple cat
        if '?' in response.url:
            page_separator = '&'
        else:
            page_separator= '?'
        page_urls = [response.url + page_separator + "page=" + str(pageNumber)
                     for pageNumber
                     in range(1, last_page_number+1)
                     ]
        # the function loops over all paginated result pages

        print '|GENERATED Links ----------|'
        print page_urls
        print '|--------------------------|'

        for page_url in page_urls:
            yield scrapy.Request(page_url, callback=self.parse_listing_results_page)
            # send a request every time and set as callback the parseQueryPage


    def parse_listing_results_page(self, response):
        for href in response.xpath('//div[@class="listing"]/@data-url').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_dir_contents)


    def parse_dir_contents(self, response):
        """
        This method extracts the actual data from the airbnb listing
        :param response: scrapy response object
        :return: item object
        """
        print "Parsing Listing: " + response.url
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
            if "+" in bathrooms: # some listings have 8+ rooms as a number
                item['bathrooms'] = 9
            else:
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

        item['neighborhood'] = response.request.url

        yield item


    def extract_filter_property(self, response):
        """
        This function takes the list of valid! filters and returns the available values found on the initial page
        :param response:
        :return: a dict with the filters as keys and the possible values as lists
        """
        filterDict = dict()

        if not self.bnb_filters:
            return filterDict
        else:
            for filter in self.bnb_filters:
                xpath_query_string = '//input[@name="%s"]/@value' % filter
                filterDict[filter] = response.xpath(xpath_query_string).extract()
            return filterDict


    def filter_dict_to_tuple(self, filter_dict):
        """
        returns a list of lists of all possible combinations of key and value to be used in the url creation
        use urllib.urlencode([first_tuple, second_tuple)]
        :param filter_dict:
        :return:
        """
        return [[(key, filter_dict[key][i]) for i in range(len(filter_dict[key]))] for key in filter_dict.keys()]


    def filter_combinations_generator(self, combinations):
        for element in itertools.product(*combinations):
            yield element


