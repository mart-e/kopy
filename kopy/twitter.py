import logging
import tweepy
from .base import BaseExtractor, Status

logger = logging.getLogger(__name__)


class TwitterExtractor(BaseExtractor):
    def parse_config(self, config):
        auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
        auth.set_access_token(config["access_token_key"], config["access_token_secret"])
        self.api = tweepy.API(auth)
        return True

    def get_statuses(self, count=10, since=None):
        return self.api.home_timeline(
            count=count,
            tweet_mode="extended",
            max_id=since and since.sid or None)

    def format_status(self, status):
        return f"""
<li>
    <strong>{status.user.name}</strong>:
    {status.text}
</li>
"""

    def convert_status(self, status):
        def text_prettify(entry):
            text = entry.full_text
            text = text.replace("\n", "<br/>")
            for entity in entry.entities["hashtags"]:
                text = text.replace(
                    f"#{entity['text']}",
                    f"<a href='https://twitter.com/hashtag/{entity['text']}' rel='nofollow noopener'"
                    f" target='_blank'>#{entity['text']}</a>",
                )
            for entity in entry.entities["urls"]:
                text = text.replace(
                    entity["url"],
                    f"<a href='{entity['expanded_url']}' rel='nofollow noopener'"
                    f" target='_blank' title='{entity['expanded_url']}'>"
                    f"{entity['display_url']}</a>",
                )
            for entity in entry.entities.get("media", []):
                text = text.replace(
                    entity["url"],
                    f"<a href='{entity['expanded_url']}' rel='nofollow noopener'"
                    f" target='_blank' title='{entity['expanded_url']}'>"
                    f"{entity['display_url']}</a>",
                )
            for entity in entry.entities["user_mentions"]:
                source = entry.full_text[entity['indices'][0]:entity['indices'][1]]
                text = text.replace(
                    source,
                    f"<a href='https://twitter.com/{entity['screen_name']}' rel='nofollow noopener'"
                    f" target='_blank'>@{entity['screen_name']}</a>",
                )
            return text

        def extract_media(entry):
            medias = []
            entities = entry.entities.get("media", [])
            if hasattr(entry, 'extended_entities'):
                entities.extend(entry.extended_entities.get("media", []))
            for entity in entities:
                if entity["type"] == "photo":
                    media = {
                        "type": "image",
                        "inline": entity["media_url_https"],
                        "url": entity["url"],
                    }
                    if media not in medias:
                        medias.append(media)
                elif entity["type"] == "video":
                    medias.append(
                        {"type": "video", "inline": entity["url"], "url": entity["url"]}
                    )
                else:
                    logger.warning(f"Ignore twitter media type {entity['type']}")
            return medias

        if hasattr(status, "retweeted_status"):
            r = status.retweeted_status
            full_text = text_prettify(r)

            retweeted_status = Status(
                sid=str(r.id),
                date=r.created_at,
                author=r.user.name,
                author_title="@"+r.user.screen_name,
                author_avatar=r.user.profile_image_url_https,
                author_url=f"https://twitter.com/{r.user.screen_name}",
                content=full_text,
                extractor=self.name,
                url=f"https://twitter.com/{r.user.screen_name}/status/{r.id}",
                reply_count=r.in_reply_to_status_id_str and 1 or 0,
                reblog_count=r.retweet_count,
                favorite_count=r.favorite_count,
                medias=extract_media(r),
            )
        else:
            retweeted_status = False

        full_text = text_prettify(status)
        return Status(
            sid=str(status.id),
            date=status.created_at,
            author=status.user.name,
            author_title="@"+status.user.screen_name,
            author_avatar=status.user.profile_image_url_https,
            author_url=f"https://twitter.com/{status.user.screen_name}",
            content=full_text,
            url=f"https://twitter.com/{status.user.screen_name}/status/{status.id}",
            extractor=self.name,
            reply_count=status.in_reply_to_status_id_str and 1 or 0,
            reblog_count=status.retweet_count,
            favorite_count=status.favorite_count,
            medias=extract_media(status),
            original_status=retweeted_status,
        )
