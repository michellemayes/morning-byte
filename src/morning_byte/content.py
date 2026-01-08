"""Content extraction for full article text."""

import asyncio
from dataclasses import dataclass

import httpx
import trafilatura

from morning_byte.models import Article

# User agent for fetching content
USER_AGENT = "MorningByte/0.1.0 (https://github.com/morning-byte)"

# Domains that typically block scrapers or have paywalls
SKIP_DOMAINS = {
    "twitter.com",
    "x.com",
    "youtube.com",
    "youtu.be",
    "github.com",
    "reddit.com",
    "news.ycombinator.com",
    "lobste.rs",
    "dev.to",
    "medium.com",
    "nytimes.com",
    "wsj.com",
    "bloomberg.com",
    "ft.com",
    "patreon.com",
    "substack.com",
}


@dataclass
class ContentResult:
    """Result of content extraction."""

    url: str
    content: str
    success: bool
    error: str = ""


async def fetch_content(url: str, timeout: float = 15.0) -> ContentResult:
    """Fetch and extract article content from a URL."""
    try:
        # Check if domain should be skipped
        from urllib.parse import urlparse

        domain = urlparse(url).netloc.replace("www.", "")
        if domain in SKIP_DOMAINS:
            return ContentResult(url=url, content="", success=False, error="Domain skipped")

        # Fetch the page
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text

        # Extract content using trafilatura
        content = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            include_images=False,
            include_links=False,
            output_format="html",
            favor_precision=True,
        )

        if content:
            return ContentResult(url=url, content=content, success=True)
        else:
            return ContentResult(
                url=url, content="", success=False, error="No content extracted"
            )

    except httpx.TimeoutException:
        return ContentResult(url=url, content="", success=False, error="Timeout")
    except httpx.HTTPStatusError as e:
        return ContentResult(
            url=url, content="", success=False, error=f"HTTP {e.response.status_code}"
        )
    except Exception as e:
        return ContentResult(url=url, content="", success=False, error=str(e))


async def fetch_articles_content(
    articles: list[Article],
    max_concurrent: int = 5,
    timeout: float = 15.0,
) -> dict[str, ContentResult]:
    """Fetch content for multiple articles concurrently.

    Args:
        articles: List of articles to fetch content for
        max_concurrent: Maximum number of concurrent requests
        timeout: Timeout per request in seconds

    Returns:
        Dictionary mapping article URLs to content results
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(article: Article) -> tuple[str, ContentResult]:
        async with semaphore:
            result = await fetch_content(article.url, timeout)
            return article.url, result

    tasks = [fetch_with_semaphore(article) for article in articles]
    results = await asyncio.gather(*tasks)

    return dict(results)


def enrich_articles_with_content(
    articles: list[Article],
    content_results: dict[str, ContentResult],
) -> list[Article]:
    """Update articles with fetched content.

    Args:
        articles: List of articles to update
        content_results: Dictionary of content results by URL

    Returns:
        List of articles (same objects, modified in place)
    """
    for article in articles:
        result = content_results.get(article.url)
        if result and result.success and result.content:
            article.content = result.content

    return articles
