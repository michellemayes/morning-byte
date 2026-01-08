"""Lobsters source - uses the public JSON API."""

from datetime import datetime

from dateutil import parser as date_parser

from morning_byte.config import SourceConfig
from morning_byte.models import Article

from .base import BaseSource


class LobstersSource(BaseSource):
    """Fetch stories from Lobsters.

    Lobsters is a computing-focused community similar to HN but with
    a stronger focus on technical content. Has a free public JSON API.
    https://lobste.rs/
    """

    name = "lobsters"
    display_name = "Lobsters"

    def __init__(self, config: SourceConfig):
        super().__init__(config)

    async def fetch(self) -> list[Article]:
        """Fetch hottest stories from Lobsters."""
        try:
            response = await self.client.get("https://lobste.rs/hottest.json")
            response.raise_for_status()
            stories = response.json()

            articles = []
            for story in stories[: self.config.max_items]:
                # Parse the ISO timestamp
                created = None
                if story.get("created_at"):
                    try:
                        created = date_parser.parse(story["created_at"])
                    except Exception:
                        created = datetime.now()

                # Lobsters uses different URL for discussion vs link
                url = story.get("url") or story.get("short_id_url", "")
                comments_url = story.get("short_id_url", "")

                articles.append(
                    Article(
                        title=story.get("title", ""),
                        url=url,
                        source=self.display_name,
                        author=story.get("submitter_user", {}).get("username", ""),
                        score=story.get("score", 0),
                        comments_count=story.get("comment_count", 0),
                        comments_url=comments_url,
                        published_at=created,
                        summary=story.get("description", ""),
                        tags=story.get("tags", []),
                    )
                )

            return articles
        except Exception:
            return []
