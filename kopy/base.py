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

    def __init__(self, date, author, content, extractor_name):
        self.date = date
        self.author = author
        self.content = content
        self.extractor = extractor_name

    def __lt__(self, other):
        return self.date < other.date

class StatusManager:

    def __init__(self):
        self._items = []

    def add(self, status):
        """ Insert a status while maintaining the order """
        bisect.insort_left(self._items, status)

    def fetch(self, count=10, desc=True, offset=0):
        pass
