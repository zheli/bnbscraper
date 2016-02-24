# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem
import logging

class MongoDBPListingsPipeline(object):


    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_LISTINGS_COLLECTION']]


    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        logging.log(logging.DEBUG, "Hosting ID %d added to database"%item['hosting_id'])
        return item
