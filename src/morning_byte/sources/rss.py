"""RSS/Atom feed source."""

import asyncio
from datetime import datetime

import feedparser
from dateutil import parser as date_parser

from morning_byte.config import SourceConfig
from morning_byte.models import Article

from .base import BaseSource


class RSSSource(BaseSource):
    """Fetch articles from RSS/Atom feeds.

    Supports any standard RSS or Atom feed. Great for following
    specific tech blogs and newsletters.
    """

    name = "rss"
    display_name = "RSS Feeds"

    def __init__(self, config: SourceConfig):
        super().__init__(config)

    async def fetch(self) -> list[Article]:
        """Fetch articles from all configured RSS feeds."""
        if not self.config.feeds:
            return []

        # Fetch all feeds in parallel
        tasks = [self._fetch_feed(feed) for feed in self.config.feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        articles = []
        for result in results:
            if isinstance(result, list):
                articles.extend(result)

        # Sort by date (newest first)
        articles.sort(key=lambda a: a.published_at or datetime.min, reverse=True)
        return articles[: self.config.max_items]

    async def _fetch_feed(self, feed_config: dict) -> list[Article]:
        """Fetch and parse a single RSS feed."""
        url = feed_config.get("url", "")
        name = feed_config.get("name", url)

        if not url:
            return []

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            # feedparser works synchronously, so we parse the content
            feed = feedparser.parse(response.text)

            articles = []
            for entry in feed.entries[:10]:  # Limit per feed
                # Parse publication date
                published = None
                for date_field in ["published", "updated", "created"]:
                    if hasattr(entry, date_field):
                        try:
                            published = date_parser.parse(getattr(entry, date_field))
                            break
                        except Exception:
                            continue

                # Get summary - prefer summary over content for brevity
                summary = ""
                if hasattr(entry, "summary"):
                    summary = self._clean_html(entry.summary)
                elif hasattr(entry, "content") and entry.content:
                    summary = self._clean_html(entry.content[0].get("value", ""))

                # Truncate long summaries
                if len(summary) > 500:
                    summary = summary[:497] + "..."

                articles.append(
                    Article(
                        title=getattr(entry, "title", "Untitled"),
                        url=getattr(entry, "link", ""),
                        source=name,
                        author=getattr(entry, "author", ""),
                        published_at=published,
                        summary=summary,
                    )
                )

            return articles
        except Exception:
            return []

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags from content."""
        from bs4 import BeautifulSoup

        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)
