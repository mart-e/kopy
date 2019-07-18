import logging

from mastodon import Mastodon
from .base import BaseExtractor, Status

logger = logging.getLogger(__name__)


class MastodonExtractor(BaseExtractor):
    def parse_config(self, config):
        self.api = Mastodon(
            client_id=config["client_id"],
            api_base_url=config["api_base_url"],
            client_secret=config["secret"],
            access_token=config["access_token"],
        )
        return True

    def _get_statuses(self, count=10, since=None):
        return self.api.timeline(
            timeline='home',
            limit=count,
            since_id=since and since.sid or None)

    def format_status(self, status):
        return f"""
<li>
    <strong>{status['account']['username']}</strong>:
    {status['content']}
</li>
"""

    def convert_status(self, status):
        def extract_media(entry):
            medias = []
            for entity in entry["media_attachments"]:
                if entity["type"] == "image":
                    medias.append(
                        {
                            "type": "image",
                            "inline": entity["preview_url"],
                            "url": entity["url"],
                        }
                    )
                elif entity["type"] in ("video", "gifv"):
                    medias.append(
                        {"type": "video", "inline": entity["url"], "url": entity["url"]}
                    )
                else:
                    logger.warning(f"Ignore mastodon media type {entity['type']}")
            return medias

        url = status["url"]
        if status["reblog"]:
            r = status["reblog"]
            url = r["url"]
            original_status = Status(
                sid=str(r["id"]),
                date=r["created_at"].replace(tzinfo=None),
                author=r["account"]["username"],
                author_title=r["account"]["acct"],
                author_avatar=r["account"].get("avatar_static") or r["account"]["avatar"],
                author_url=r["account"]["url"],
                content=r["content"],
                url=url,
                extractor=self.name,
                reblog_count=r['reblogs_count'],
                favorite_count=r['favourites_count'],
                reply_count=r['replies_count'],
                medias=extract_media(r),
            )
        else:
            original_status = False

        return Status(
            sid=str(status["id"]),
            date=status["created_at"].replace(tzinfo=None),
            author=status["account"]["username"],
            author_title=status["account"]["acct"],
            author_avatar=status["account"].get("avatar_static") or status["account"]["avatar"],
            author_url=status["account"]["url"],
            content=status["content"],
            url=url,
            original_status=original_status,
            extractor=self.name,
            reblog_count=status['reblogs_count'],
            favorite_count=status['favourites_count'],
            reply_count=status['replies_count'],
            medias=(
                original_status and original_status.medias or extract_media(status)
            ),
        )
