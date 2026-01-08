"""Dev.to source - uses the free public API."""

import asyncio
from datetime import datetime

from dateutil import parser as date_parser

from morning_byte.config import SourceConfig
from morning_byte.models import Article

from .base import BaseSource


class DevToSource(BaseSource):
    """Fetch articles from Dev.to.

    Dev.to has a free public API with no auth required for reading.
    https://developers.forem.com/api
    """

    name = "devto"
    display_name = "Dev.to"

    BASE_URL = "https://dev.to/api"

    def __init__(self, config: SourceConfig):
        super().__init__(config)

    async def fetch(self) -> list[Article]:
        """Fetch top articles from Dev.to."""
        if self.config.tags:
            # Fetch from specific tags
            tasks = [self._fetch_tag(tag) for tag in self.config.tags]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            articles = []
            for result in results:
                if isinstance(result, list):
                    articles.extend(result)

            # Deduplicate by URL and sort by reactions
            seen_urls = set()
            unique_articles = []
            for article in sorted(articles, key=lambda a: a.score, reverse=True):
                if article.url not in seen_urls:
                    seen_urls.add(article.url)
                    unique_articles.append(article)

            return unique_articles[: self.config.max_items]
        else:
            # Fetch top articles
            return await self._fetch_top()

    async def _fetch_top(self) -> list[Article]:
        """Fetch top articles."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/articles",
                params={"per_page": self.config.max_items, "top": 1},  # Top from last day
            )
            response.raise_for_status()
            return self._parse_articles(response.json())
        except Exception:
            return []

    async def _fetch_tag(self, tag: str) -> list[Article]:
        """Fetch articles for a specific tag."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/articles",
                params={"tag": tag, "per_page": 10, "top": 1},
            )
            response.raise_for_status()
            return self._parse_articles(response.json())
        except Exception:
            return []

    def _parse_articles(self, data: list) -> list[Article]:
        """Parse article data from API response."""
        articles = []
        for item in data:
            published = None
            if item.get("published_at"):
                try:
                    published = date_parser.parse(item["published_at"])
                except Exception:
                    published = datetime.now()

            articles.append(
                Article(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    source=self.display_name,
                    author=item.get("user", {}).get("username", ""),
                    score=item.get("positive_reactions_count", 0),
                    comments_count=item.get("comments_count", 0),
                    comments_url=item.get("url", ""),
                    published_at=published,
                    summary=item.get("description", ""),
                    tags=item.get("tag_list", []),
                )
            )

        return articles
