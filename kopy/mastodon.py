from mastodon import Mastodon
from .base import BaseExtractor


class MastodonExtractor(BaseExtractor):

    def parse_config(self, config):
        self.api = Mastodon(client_id=config['client_id'],
                            api_base_url=config['api_base_url'],
                            client_secret=config['secret'],
                            access_token=config['access_token'])
        return True

    def get_statuses(self, count=10):
        toots = self.api.timeline_home(limit=count)
        return toots

    def format_status(self, status):
        return f"""
<li>
    <strong>{status['account']['username']}</strong>:
    {status['content']}
</li>
"""

    def unify_status_format(self, status):
        return {
            'date': status['date'],
            'author': status['account']['username'],
            'content': status['content'],
        }
