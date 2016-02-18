import scrapy
from bnbscraper.bnbItem import BnbItem
import json

# startUrls = ["https://www.airbnb.com/s/Lucca--Italy?&page="+str(pageNumber) for pageNumber in range(1, 17)]
startUrls = ["https://www.airbnb.com/s/Reggio-Emilia--Italy?&page="+str(pageNumber) for pageNumber in range(1, 2)]

class AirbnbSpider(scrapy.Spider):
    name = "airbnb"
    allowed_domains = ["airbnb.com"]
    start_urls = startUrls

    def parse(self, response):
        for href in response.xpath('//div[@class="listing"]/@data-url').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_dir_contents)


    def parse_dir_contents(self, response):
        item = BnbItem()
        airbn_json_all = json.loads(response.xpath('//meta[@id="_bootstrap-room_options"]/@content').extract()[0])
        airbnb_json = airbn_json_all['airEventData']
        item['rev_count'] = airbnb_json['visible_review_count']
        item['amenities'] = airbnb_json['amenities']
        item['host_id'] = airbn_json_all['hostId']
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
        item['reponse_rate'] = airbnb_json['reponse_rate_shown']
        item['title'] = response.xpath('/html/head/meta[@property="og:title"]/@content').extract()
        item['location'] = response.xpath('/html/head/meta[@property="airbedandbreakfast:locality"]/@content').extract()
        item['region'] = response.xpath('/html/head/meta[@property="airbedandbreakfast:region"]/@content').extract()
        item['country'] = response.xpath('/html/head/meta[@property="airbedandbreakfast:country"]/@content').extract()
        item['lat'] = response.xpath('/html/head/meta[@property="airbedandbreakfast:location:latitude"]/@content').extract()
        item['lng'] = response.xpath('/html/head/meta[@property="airbedandbreakfast:location:longitude"]/@content').extract()
        item['url'] = response.url
        item['bathrooms'] = response.xpath('//strong[contains(@data-reactid,"Bathrooms")]/text()').extract()
        item['bedrooms'] = response.xpath('//strong[contains(@data-reactid,"Bedrooms")]/text()').extract()
        item['beds'] = response.xpath('//strong[contains(@data-reactid,"Beds")]/text()').extract()
        item['propertyType'] = response.xpath('//strong[contains(@data-reactid,"Property type")]/text()').extract()
        item['extraPeople'] = response.xpath('//strong[contains(@data-reactid,"Extra people")]/text()').extract()
        item['cleaningFee'] = response.xpath('//strong[contains(@data-reactid,"Cleaning")]/text()').extract()

        yield item
