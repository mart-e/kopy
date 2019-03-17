import tweepy
from .base import BaseExtractor, Status


class TwitterExtractor(BaseExtractor):

    def parse_config(self, config):
        auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
        auth.set_access_token(config['access_token_key'], config['access_token_secret'])
        self.api = tweepy.API(auth)
        return True

    def get_statuses(self, count=10):
        public_tweets = self.api.home_timeline(count=count, tweet_mode='extended')
        return public_tweets

    def format_status(self, status):
        return f"""
<li>
    <strong>{status.user.name}</strong>:
    {status.text}
</li>
"""
    def convert_status(self, status):
        def replace_urls(entry):
            text = entry.full_text
            for entity in entry.entities['urls']:
                text = text.replace(
                    entity['url'],
                    f"<a href='{entity['expanded_url']}'>{entity['display_url']}</a>"
                )
            for entity in entry.entities.get('media', []):
                text = text.replace(
                    entity['url'],
                    f"<a href='{entity['expanded_url']}'>{entity['display_url']}</a>"
                )
            return text

        if hasattr(status, 'retweeted_status'):
            r = status.retweeted_status
            full_text = replace_urls(r)

            retweeted_status = Status(
                sid=r.id,
                date=r.created_at,
                author=r.user.name,
                author_avatar=r.user.profile_image_url_https,
                author_url=f"https://twitter.com/{r.user.screen_name}",
                content=full_text,
                extractor=self.name,
                url=f"https://twitter.com/{r.user.screen_name}/status/{r.id}"
            )
        else:
            retweeted_status = False

        full_text = replace_urls(status)
        return Status(
            sid=status.id,
            date=status.created_at,
            author=status.user.name,
            author_avatar=status.user.profile_image_url_https,
            author_url=f"https://twitter.com/{status.user.screen_name}",
            content=full_text,
            url=f"https://twitter.com/{status.user.screen_name}/status/{status.id}",
            original_status=retweeted_status,
            extractor=self.name,
        )
