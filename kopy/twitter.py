import tweepy
from .base import BaseExtractor


class TwitterExtractor(BaseExtractor):

    def parse_config(self, config):
        auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
        auth.set_access_token(config['access_token_key'], config['access_token_secret'])
        self.api = tweepy.API(auth)
        return True

    def get_statuses(self, count=10):
        public_tweets = self.api.home_timeline(count=count)
        return public_tweets

    def format_status(self, status):
        return f"""
<li>
    <strong>{status.user.name}</strong>:
    {status.text}
</li>
"""
    def unify_status_format(self, status):
        return {
            'date': status.date,
            'author': status.user.name,
            'content': status.text,
        }
