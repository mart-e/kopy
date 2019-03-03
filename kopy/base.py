import bisect

class BaseExtractor:

    def __init__(self, name):
        self.name = name

    def parse_config(self, config):
        """
        Parse the config to generate a new extractor
        Connection to remote server must be setup and ready to call methods such
        as `get_statuses` after
        """
        raise NotImplementedError

    def get_statuses(self, count=10):
        """
        Retrieve the `count` latest statuses in the main timeline
        """
        raise NotImplementedError

    def format_status(self, status):
        """
        From a status item (internal implementation) returns a string for display
        """
        raise NotImplementedError

    def convert_status(self, status):
        """
        From a status item (internal implementation) returns a Status object
        """
        raise NotImplementedError

class Status:

    def __init__(self, sid, date, author, author_avatar,
        content, url, extractor):
        self.sid = sid
        self.date = date
        self.author = author
        self.author_avatar = author_avatar
        self.content = content
        self.url = url
        self.extractor = extractor

    def __lt__(self, other):
        return self.date < other.date

class StatusManager:

    def __init__(self):
        self.items = []
        self.extractors = []

    def add(self, status):
        """ Insert a status while maintaining the order """
        index = bisect.bisect(self.items, status)
        if index == 0 or self.items[index-1].sid != status.sid:
            self.items.insert(index, status)

    def fetch(self, count=10, offset=0):
        res = []
        index = len(self.items) - 1 - offset
        while index > 0:
            res.append( self.items[index] )
            index -= 1
        return res
