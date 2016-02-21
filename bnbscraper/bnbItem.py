import scrapy


class BnbItem(scrapy.Item):
        rev_count = scrapy.Field()
        amenities = scrapy.Field()
        host_id = scrapy.Field()
        hosting_id = scrapy.Field()
        room_type = scrapy.Field()
        price = scrapy.Field()
        bed_type = scrapy.Field()
        person_capacity = scrapy.Field()
        cancel_policy = scrapy.Field()
        rating_communication = scrapy.Field()
        rating_cleanliness = scrapy.Field()
        rating_checkin = scrapy.Field()
        satisfaction_guest = scrapy.Field()
        instant_book = scrapy.Field()
        accuracy_rating = scrapy.Field()
        response_time = scrapy.Field()
        response_rate = scrapy.Field()
        title = scrapy.Field()
        location = scrapy.Field()
        region = scrapy.Field()
        country = scrapy.Field()
        lat = scrapy.Field()
        lng = scrapy.Field()
        url = scrapy.Field()
        bathrooms = scrapy.Field()
        bedrooms = scrapy.Field()
        beds = scrapy.Field()
        propertyType = scrapy.Field()
        extraPeople = scrapy.Field()
        cleaningFee = scrapy.Field()
        pageNumber = scrapy.Field()
        neighborhood = scrapy.Field()
        iso_state_json = scrapy.Field()
