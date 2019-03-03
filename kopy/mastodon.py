from mastodon import Mastodon
from .base import BaseExtractor, Status


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

    def convert_status(self, status):
        return Status(
            sid=status['id'],
            date=status['created_at'].replace(tzinfo=None),
            author=status['account']['username'],
            author_avatar=status['account']['avatar'],
            content=status['content'],
            url=status['url'],
            extractor=self.name,
        )
