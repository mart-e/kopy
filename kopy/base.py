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

    def __init__(self, sid, date,
            author, author_avatar, author_url,
            content, url, extractor, medias=False,
            original_status=False):
        self.sid = sid
        self.date = date
        self.timestamp = int(date.timestamp())
        self.author = author
        self.author_avatar = author_avatar
        self.author_url = author_url
        self.content = content
        self.url = url
        self.extractor = extractor
        self.original_status = original_status

        self.is_r = bool(self.original_status)
        self.r_author = self.original_status.author if self.original_status \
                        else self.author
        self.r_author_avatar = self.original_status.author_avatar if self.original_status \
                               else self.author_avatar
        self.r_author_url = self.original_status.author_url if self.original_status \
                            else self.author_url
        self.r_content = self.original_status.content if self.original_status \
                         else self.content

        self.medias = medias or []

    def __lt__(self, other):
        return self.date < other.date

    def export_to_json(self):
        return {
            'sid': self.sid,
            'date': self.date,
            'timestamp': self.timestamp,
            'author': self.author,
            'author_avatar': self.author_avatar,
            'author_url': self.author_url,
            'content': self.content,
            'url': self.url,
            'extractor': self.extractor,
            'original_status': self.original_status and self.original_status.export_to_json(),
            'is_r': self.is_r,
            'r_author': self.r_author,
            'r_author_avatar': self.r_author_avatar,
            'r_author_url': self.r_author_url,
            'r_content': self.r_content,
            'medias': self.medias,
        }

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
            res.append(self.items[index])
            index -= 1
        return res

    def export_to_json(self):
        res = []
        for status in self.fetch():
            res.append(
                status.export_to_json()
            )
        return res
