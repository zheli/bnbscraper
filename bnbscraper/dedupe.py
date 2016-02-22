import os

from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.request import request_fingerprint

class CustomFilter(RFPDupeFilter):
    """A dupe filter that considers specific ids in the url"""

    def __getid(self, url):
        if 'room' in url:
            mm = url.split('/rooms/')[1].split('?')[0]
            return mm
        else:
            return None

    def request_seen(self, request):
        fp = self.__getid(request.url)
        if fp in self.fingerprints and fp:
            print 'DEDUPE: '+fp
            return True
        self.fingerprints.add(fp)
        if self.file:
            self.file.write(fp + os.linesep)