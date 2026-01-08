"""Reddit source - uses the public JSON API (no auth required for reading)."""

import asyncio
from datetime import datetime

from morning_byte.config import SourceConfig
from morning_byte.models import Article

from .base import BaseSource


class RedditSource(BaseSource):
    """Fetch top posts from Reddit subreddits.

    Uses Reddit's public JSON API which doesn't require authentication
    for read-only access. Just append .json to any Reddit URL.
    """

    name = "reddit"
    display_name = "Reddit"

    def __init__(self, config: SourceConfig):
        super().__init__(config)
        # Reddit requires a more specific User-Agent
        self.client.headers["User-Agent"] = (
            "MorningByte/0.1.0 (Daily tech digest; contact@example.com)"
        )

    async def fetch(self) -> list[Article]:
        """Fetch top posts from configured subreddits."""
        if not self.config.subreddits:
            return []

        # Fetch from each subreddit in parallel
        tasks = [
            self._fetch_subreddit(sub) for sub in self.config.subreddits
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        articles = []
        for result in results:
            if isinstance(result, list):
                articles.extend(result)

        # Sort by score and limit
        articles.sort(key=lambda a: a.score, reverse=True)
        return articles[: self.config.max_items]

    async def _fetch_subreddit(self, subreddit: str) -> list[Article]:
        """Fetch top posts from a single subreddit."""
        try:
            # Get hot posts from the last day
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25&t=day"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()

            articles = []
            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})

                # Skip stickied posts and self-posts without much content
                if post_data.get("stickied"):
                    continue

                # Determine URL - use external link if available, otherwise Reddit post
                url = post_data.get("url", "")
                is_self = post_data.get("is_self", False)
                permalink = f"https://www.reddit.com{post_data.get('permalink', '')}"

                if is_self or not url or url.startswith("https://www.reddit.com"):
                    url = permalink

                # Get summary from selftext or empty
                summary = ""
                if is_self:
                    selftext = post_data.get("selftext", "")
                    if selftext:
                        # Truncate long self posts
                        summary = selftext[:500] + "..." if len(selftext) > 500 else selftext

                articles.append(
                    Article(
                        title=post_data.get("title", ""),
                        url=url,
                        source=f"r/{subreddit}",
                        author=post_data.get("author", ""),
                        score=post_data.get("score", 0),
                        comments_count=post_data.get("num_comments", 0),
                        comments_url=permalink,
                        published_at=datetime.fromtimestamp(post_data.get("created_utc", 0)),
                        summary=summary,
                        tags=[subreddit],
                    )
                )

            return articles
        except Exception:
            return []
