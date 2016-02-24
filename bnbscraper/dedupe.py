import os
import pymongo

from scrapy.conf import settings
from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.request import request_fingerprint
import logging






class CustomFilter(RFPDupeFilter):
    """A dupe filter that considers specific ids in the url"""

    def __init__(self,*args, **kwargs):
        super(CustomFilter, self).__init__(*args, **kwargs)
        # set up pymongo connections
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_LISTINGS_COLLECTION']]


    def __getid(self, url):
        if 'room' in url:
            mm = url.split('/rooms/')[1].split('?')[0]
            return float(mm)
        else:
            return 0

    def request_seen(self, request):
        hosting_id = self.__getid(request.url)

        if self.collection.find_one({'hosting_id': hosting_id}):
            logging.log(logging.DEBUG, "Hosting ID %d seen twice"%hosting_id)
            return True

