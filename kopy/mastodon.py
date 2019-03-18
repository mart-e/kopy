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
        url = status['url']
        if status['reblog']:
            r = status['reblog']
            url = r['url']
            original_status = Status(
                sid=r['id'],
                date=r['created_at'].replace(tzinfo=None),
                author=r['account']['username'],
                author_avatar=r['account']['avatar'],
                author_url=r['account']['url'],
                content=r['content'],
                url=url,
                extractor=self.name,
            )
        else:
            original_status = False

        return Status(
            sid=status['id'],
            date=status['created_at'].replace(tzinfo=None),
            author=status['account']['username'],
            author_avatar=status['account']['avatar'],
            author_url=status['account']['url'],
            content=status['content'],
            url=url,
            original_status=original_status,
            extractor=self.name,
        )
