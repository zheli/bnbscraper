import scrapy
from bnbscraper.bnbItem import BnbItem
import json
import itertools
import time
import logging

AIRBNB_URL = "https://www.airbnb.com/s/"


class AirbnbSpider(scrapy.Spider):
    """
    pass command line arguments as follows
    e.g. scrapy crawl airbnb -a query=Reggio-Emilia--Italy filters=neighborhood,propertytype-o tests.json
    """

    def __init__(self, query='', filters='', *args, **kwargs):
        super(AirbnbSpider, self).__init__(*args, **kwargs)
        self.start_urls = [AIRBNB_URL + query]
        self.bnb_filters = [b_filter.strip() for b_filter in list(filters.split(','))]

    name = "airbnb"
    allowed_domains = ["airbnb.com"]

    def parse(self, response):
        filter_dict = self.extract_filter_property(response)
        # test if there are any neighborhoods
        if not filter_dict:
            # if not pass the first page to the parse result page
            yield scrapy.Request(self.start_urls[0], callback=self.parse_start_page)
        else:
            request_urls = []
            filter_tuples = self.filter_dict_to_tuple(filter_dict)
            for cartesian_combination in self.filter_combinations_generator(filter_tuples):
                for power_combination in self.power_set(cartesian_combination):
                    query_string = '&'.join([k + '=' + v for k, v in power_combination])
                    request_url = self.start_urls[0] + '?' + query_string
                    request_urls.append(request_url)

            logging.log(logging.DEBUG ,'Duplicate Request urls: ' + str(len(request_urls)))
            request_urls = set(request_urls)
            logging.log(logging.DEBUG ,'DeDuplicated Request urls: ' + str(len(request_urls)))
            request_urls = list(request_urls)
            request_urls.sort(key = len)
            self.filter_urls = request_urls

            while self.filter_urls:
                filter_request_url = self.filter_urls.pop(0)
                max_page_number = scrapy.Request(filter_request_url, callback=self.last_pagenumer_in_search)
                if max_page_number == 0:
                   len_before = len(self.filter_urls)
                   self.filter_urls = filter(lambda url: not filter_request_url in url, self.filter_urls)
                   len_after= len(self.filter_urls)
                   logging.log(logging.DEBUG, "Page: {0} has 0 results reduce urls from {1} to {2}".format(
                                                        filter_request_url,
                                                        str(len_before),
                                                        str(len_after)
                                                        )
                                )
                elif max_page_number < 17:
                   len_before = len(self.filter_urls)
                   self.filter_urls = filter(lambda url: not filter_request_url in url, self.filter_urls)
                   len_after = len(self.filter_urls)
                   logging.log(logging.DEBUG, "Page: {0} has {3} results reduce urls from {1} to {2}".format(
                                                        filter_request_url,
                                                        str(len_before),
                                                        str(len_after),
                                                        str(max_page_number)
                                                        )
                                )
                   yield scrapy.Request(filter_request_url, callback=self.parse_start_page)
                else:
                    logging.log(logging.DEBUG, "Page: {0} has 17+ results.".format(filter_request_url))
                    yield scrapy.Request(filter_request_url, callback=self.parse_start_page)



    def parse_start_page(self, response):
        """
        this function is called to parse the individual links on
        the result page after any filter in the previous steps
        :param response:
        :return:
        """
        last_page_number = self.last_pagenumer_in_search(response)
        if last_page_number > 16: logging.log(logging.INFO, "There are {0} pages on: {1}".format(str(last_page_number), response.url))

        if '?' in response.url:
            page_separator = '&'
        else:
            page_separator = '?'

        page_urls = [response.url + page_separator + "page=" + str(pageNumber)
                                for pageNumber in range(1, last_page_number + 1)]


        for page_url in page_urls:
            yield scrapy.Request(page_url, callback=self.parse_listing_results_page)





    def parse_listing_results_page(self, response):
        for href in response.xpath('//div[@class="listing"]/@data-url').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_listing_contents)

    def parse_listing_contents(self, response):
        """
        This method extracts the actual data from the airbnb listing
        :param response: scrapy response object
        :return: item object
        """
        item = BnbItem()

        json_array = response.xpath('//meta[@id="_bootstrap-room_options"]/@content').extract();
        if json_array:
            airbnb_json_all = json.loads(json_array[0])
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
            item['calendarLastUpdated'] = airbnb_json_all['calendarLastUpdated']
            item['nightly_price'] = airbnb_json_all['nightly_price']
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

        city = response.xpath('/html/head/meta[@property="airbedandbreakfast:city"]/@content').extract()
        if len(country):
            item['city'] = city[0]

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
            if "+" in bathrooms[0]:  # some listings have 8+ rooms as a number
                item['bathrooms'] = 9
            else:
                item['bathrooms'] = float(bathrooms[0])

        bedrooms = response.xpath('//strong[contains(@data-reactid,"Bedrooms")]/text()').extract()
        if len(bedrooms):
            item['bedrooms'] = float(bedrooms[0])

        beds = response.xpath('//strong[contains(@data-reactid,"Beds")]/text()').extract()
        if len(beds):
            item['beds'] = float(beds[0])

        property_type = response.xpath('//strong[contains(@data-reactid,"Property type")]/text()').extract()
        if len(property_type):
            item['propertyType'] = property_type[0]

        extra_people = response.xpath('//strong[contains(@data-reactid,"Extra people")]/text()').extract()
        if len(extra_people):
            item['extraPeople'] = extra_people[0]

        cleaning_fee = response.xpath('//strong[contains(@data-reactid,"Cleaning")]/text()').extract()
        if len(cleaning_fee):
            item['cleaningFee'] = cleaning_fee[0]


        host_link = response.xpath("//a[contains(@href, '/users/show/')]/@href").extract()
        if host_link:
            item['host_url'] = response.urljoin(host_link[0])

        item['scraped_time'] = time.time()

        yield item






    def extract_filter_property(self, response):
        """
        This function takes the list of valid! filters and returns the available values found on the initial page
        :param response:
        :return: a dict with the filters as keys and the possible values as lists
        """
        filter_dict = dict()

        if not self.bnb_filters:
            return filter_dict
        else:
            for b_filter in self.bnb_filters:
                xpath_query_string = '//input[@name="%s"]/@value' % b_filter
                filter_values = response.xpath(xpath_query_string).extract()
                if not filter_values:  # check if the provided filter is even available
                    continue
                else:
                    filter_dict[b_filter] = filter_values
            return filter_dict


    def last_pagenumer_in_search(self, response):
        """
        the function takes a response from a search result page and returns the last page number:
        if the page does not contain any results it returns 0
        if the page contains only one page then it returns 1
        if the page contains more then 1 page it returns that number
        :param response: response from a results page
        """
        try:
            last_page_number = int(response
                                   .xpath('//ul[@class="list-unstyled"]/li[last()-1]/a/@href')
                                   .extract()[0]
                                   .split('page=')[1]
                                   )
            return last_page_number

        except IndexError:
            reason = response.xpath('//p[@class="text-lead"]/text()').extract()
            if reason and ('find any results that matched your criteria' in reason[0]):
                logging.log(logging.DEBUG,'No results on page'+response.url )
                return 0
            else:
                return 1


    @staticmethod
    def filter_dict_to_tuple(filter_dict):
        """
        returns a list of lists of all possible combinations of key and value to be used in the url creation
        :param filter_dict:
        :return:
        """
        return [[(key, filter_dict[key][i]) for i in range(len(filter_dict[key]))] for key in filter_dict.keys()]

    @staticmethod
    def filter_combinations_generator(combinations):
        for element in itertools.product(*combinations):
            yield element


    @staticmethod
    def power_set(iterable):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))