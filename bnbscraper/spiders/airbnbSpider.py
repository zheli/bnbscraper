import scrapy
from bnbscraper.bnbItem import BnbItem


# startUrls = ["https://www.airbnb.com/s/Lucca--Italy?&page="+str(pageNumber) for pageNumber in range(1, 17)]
startUrls = ["https://www.airbnb.com/s/Reggio-Emilia--Italy?&page="+str(pageNumber) for pageNumber in range(1, 17)]

class AirbnbSpider(scrapy.Spider):
    name = "airbnb"
    allowed_domains = ["airbnb.com"]
    start_urls = startUrls

    def parse(self, response):
        for href in response.xpath('//div[contains(@data-url, "rooms")]/@data-url').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_dir_contents)


    def parse_dir_contents(self, response):
            item = BnbItem()
            item['title'] = response.xpath('/html/head/meta[@property="og:title"]/@content').extract()
            item['location'] = response.xpath('/html/head/meta[@property="airbedandbreakfast:locality"]/@content').extract()
            item['region'] = response.xpath('/html/head/meta[@property="airbedandbreakfast:region"]/@content').extract()
            item['country'] = response.xpath('/html/head/meta[@property="airbedandbreakfast:country"]/@content').extract()
            item['lat'] = response.xpath('/html/head/meta[@property="airbedandbreakfast:location:latitude"]/@content').extract()
            item['long'] = response.xpath('/html/head/meta[@property="airbedandbreakfast:location:longitude"]/@content').extract()
            item['url'] = response.xpath('/html/head/meta[@property="og:url"]/@content').extract()
            item['rating'] = response.xpath('/html/head/meta[@property="airbedandbreakfast:rating"]/@content').extract()
            item['accomodates'] = response.xpath('//strong[contains(@data-reactid,"Accommodates")]/text()').extract()
            item['bathrooms'] = response.xpath('//strong[contains(@data-reactid,"Bathrooms")]/text()').extract()
            item['bedrooms'] = response.xpath('//strong[contains(@data-reactid,"Bedrooms")]/text()').extract()
            item['beds'] = response.xpath('//strong[contains(@data-reactid,"Beds")]/text()').extract()
            item['propertyType'] = response.xpath('//strong[contains(@data-reactid,"Property type")]/text()').extract()
            item['roomType'] = response.xpath('//strong[contains(@data-reactid,"Room type")]/text()').extract()
            item['extraPeople'] = response.xpath('//strong[contains(@data-reactid,"Extra people")]/text()').extract()
            item['cleaningFee'] = response.xpath('//strong[contains(@data-reactid,"Cleaning")]/text()').extract()
            item['price'] = response.xpath('//div/span[contains(@class, "price-amount")]/text()').extract()
            yield item
