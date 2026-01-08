"""News source fetchers for Morning Byte."""

from .base import BaseSource
from .devto import DevToSource
from .hackernews import HackerNewsSource
from .lobsters import LobstersSource
from .reddit import RedditSource
from .rss import RSSSource

__all__ = [
    "BaseSource",
    "HackerNewsSource",
    "RedditSource",
    "LobstersSource",
    "DevToSource",
    "RSSSource",
]

# Source registry
SOURCES: dict[str, type[BaseSource]] = {
    "hackernews": HackerNewsSource,
    "reddit": RedditSource,
    "lobsters": LobstersSource,
    "devto": DevToSource,
    "rss": RSSSource,
}


def get_source(name: str) -> type[BaseSource] | None:
    """Get a source class by name."""
    return SOURCES.get(name)
