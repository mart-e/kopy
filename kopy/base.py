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

    def unify_status_format(self, status):
        """
        From a status item (internal implementation) returns a dictionnary with
        the following format:
        {
            'date': <timestamp>,
            'author': <string>,
            'content': <string>,
        }
        """
        raise NotImplementedError

class StatusManager:

    def __init__(self):
        self.items = []
