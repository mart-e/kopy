import bisect
from datetime import timedelta


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
    def __init__(self, **kwargs):
        prop_defaults = {
            "sid": None,
            "date": None,
            "author": "",
            "author_title": "",
            "author_avatar": "",
            "author_url": "",
            "content": "",
            "url": "",
            "extractor": "base",
            "reply_count": 0,
            "reblog_count": 0,
            "favorite_count": 0,
            "medias": [],
            "original_status": None,
            "blank": False,
        }

        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))

        self.is_r = bool(self.original_status)
        r_proprieties = [
            "author",
            "author_avatar",
            "author_avatar",
            "author_title",
            "author_url",
            "content",
        ]
        for prop in r_proprieties:
            if self.is_r:
                setattr(self, "r_" + prop, getattr(self.original_status, prop))
            else:
                setattr(self, "r_" + prop, getattr(self, prop))
        if self.is_r:
            self.medias = self.original_status.medias

        if self.date:
            self.timestamp = int(self.date.timestamp())

    def __lt__(self, other):
        return self.date < other.date

    def export_to_json(self):
        to_export = [
            "sid",
            "date",
            "timestamp",
            "author",
            "author_title",
            "author_avatar",
            "author_url",
            "content",
            "url",
            "extractor",
            "is_r",
            "r_author",
            "r_author_title",
            "r_author_avatar",
            "r_author_url",
            "r_content",
            "reply_count",
            "reblog_count",
            "favorite_count",
            "medias",
            "blank",
        ]
        res = {key: getattr(self, key) for key in to_export}
        res["original_status"] = (
            self.original_status and self.original_status.export_to_json()
        )
        return res


class StatusManager:
    def __init__(self):
        self.items = []
        self.extractors = []

    def add(self, status):
        """ Insert a status while maintaining the order """
        index = bisect.bisect(self.items, status)
        if index == 0 or self.items[index - 1].sid != status.sid:
            self.items.insert(index, status)
            return index
        return False

    def retrieve_statuses(self, extractor, count=10, since=None):
        statuses = extractor.get_statuses(count, since=since)
        last = False
        for status in statuses:
            idx = self.add(extractor.convert_status(status))
            if idx is not False:
                last = self.items[idx]
        gap_status = Status(blank=True, date=last.date - timedelta(microseconds=1))
        self.add(gap_status)

    def fetch(self, count=10, offset=0):
        res = []
        index = len(self.items) - 1 - offset
        while index > 0:
            res.append(self.items[index])
            index -= 1
        return res

    def export_to_json(self):
        res = []
        for status in self.fetch():
            res.append(status.export_to_json())
        return res
