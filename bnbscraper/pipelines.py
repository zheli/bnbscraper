# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class BnbscraperPipeline(object):
    def process_item(self, item, spider):

        # TODO: Federica implement item checking logic:
        # - keep track of pages visited and drop item
        #   - possibly create an entry in a log file
        #   logFile = open('./droppedItems.log', 'a')
        #   logFile.write('Item dropped ListingID: %d, url: %s' % (id, url))
        # if you are feeling adventurous you could write to an SQL database

        return item
