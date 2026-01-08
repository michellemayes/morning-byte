"""Hacker News source - uses the free official API."""

import asyncio
from datetime import datetime

from morning_byte.config import SourceConfig
from morning_byte.models import Article

from .base import BaseSource


class HackerNewsSource(BaseSource):
    """Fetch top stories from Hacker News.

    Uses the official HN API which is completely free and requires no auth.
    https://github.com/HackerNews/API
    """

    name = "hackernews"
    display_name = "Hacker News"

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, config: SourceConfig):
        super().__init__(config)

    async def fetch(self) -> list[Article]:
        """Fetch top stories from Hacker News."""
        # Get top story IDs
        response = await self.client.get(f"{self.BASE_URL}/topstories.json")
        response.raise_for_status()
        story_ids = response.json()[: self.config.max_items]

        # Fetch story details in parallel
        tasks = [self._fetch_story(story_id) for story_id in story_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        articles = []
        for result in results:
            if isinstance(result, Article):
                articles.append(result)

        # Sort by score
        articles.sort(key=lambda a: a.score, reverse=True)
        return articles

    async def _fetch_story(self, story_id: int) -> Article | None:
        """Fetch a single story by ID."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/item/{story_id}.json")
            response.raise_for_status()
            data = response.json()

            if not data or data.get("type") != "story":
                return None

            # Handle "Ask HN" and "Show HN" posts that don't have external URLs
            url = data.get("url", f"https://news.ycombinator.com/item?id={story_id}")

            return Article(
                title=data.get("title", ""),
                url=url,
                source=self.display_name,
                author=data.get("by", ""),
                score=data.get("score", 0),
                comments_count=data.get("descendants", 0),
                comments_url=f"https://news.ycombinator.com/item?id={story_id}",
                published_at=datetime.fromtimestamp(data.get("time", 0)),
                summary=data.get("text", ""),  # For Ask HN posts
            )
        except Exception:
            return None
