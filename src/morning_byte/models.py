"""Data models for Morning Byte."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Article:
    """Represents a news article or story."""

    title: str
    url: str
    source: str
    summary: str = ""
    author: str = ""
    score: int = 0
    comments_count: int = 0
    comments_url: str = ""
    published_at: datetime | None = None
    tags: list[str] = field(default_factory=list)
    content: str = ""  # Full content if available

    def __post_init__(self):
        if self.published_at is None:
            self.published_at = datetime.now()

    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse

        try:
            parsed = urlparse(self.url)
            return parsed.netloc.replace("www.", "")
        except Exception:
            return ""


@dataclass
class Section:
    """A section in the digest (e.g., 'Top Stories', 'AI News')."""

    title: str
    articles: list[Article] = field(default_factory=list)
    description: str = ""


@dataclass
class Digest:
    """The complete daily digest."""

    title: str
    date: datetime
    sections: list[Section] = field(default_factory=list)
    intro: str = ""

    @property
    def total_articles(self) -> int:
        return sum(len(s.articles) for s in self.sections)
