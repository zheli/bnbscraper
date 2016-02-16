import scrapy


class BnbItem(scrapy.Item):
    title = scrapy.Field()  # '/html/head/meta[@property="og:title"]/@content'
    location = scrapy.Field() # '/html/head/meta[@property="airbedandbreakfast:locality"]/@content'
    region = scrapy.Field() # '/html/head/meta[@property="airbedandbreakfast:region"]/@content'
    country = scrapy.Field() # '/html/head/meta[@property="airbedandbreakfast:country"]/@content'
    lat = scrapy.Field()  # '/html/head/meta[@property="airbedandbreakfast:location:latitude"]/@content'
    long = scrapy.Field()  # '/html/head/meta[@property="airbedandbreakfast:location:longitude"]/@content'
    url = scrapy.Field()  # xpath '/html/head/meta[@property="og:url"]/@content'
    rating = scrapy.Field()  # '/html/head/meta[@property="airbedandbreakfast:rating"]/@content'
    accomodates = scrapy.Field()  # '//strong[contains(@data-reactid,"Accommodates")]/text()'
    bathrooms = scrapy.Field()  # '//strong[contains(@data-reactid,"Bathrooms")]/text()'
    bedrooms = scrapy.Field()  # '//strong[contains(@data-reactid,"Bedrooms")]/text()'
    beds = scrapy.Field()  # '//strong[contains(@data-reactid,"Beds")]/text()'
    propertyType = scrapy.Field()  # '//strong[contains(@data-reactid,"Property type")]/text()'
    roomType = scrapy.Field()   # '//strong[contains(@data-reactid,"Room type")]/text()'
    extraPeople = scrapy.Field()  # '//strong[contains(@data-reactid,"Extra people")]/text()'
    cleaningFee = scrapy.Field()  # '//strong[contains(@data-reactid,"Cleaning")]/text()'
    price = scrapy.Field()  # '//div/span[contains(@class, "price-amount")]/text()'
