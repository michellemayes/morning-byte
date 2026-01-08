"""Base class for news sources."""

from abc import ABC, abstractmethod

import httpx

from morning_byte.config import SourceConfig
from morning_byte.models import Article


class BaseSource(ABC):
    """Abstract base class for news sources."""

    name: str = "base"
    display_name: str = "Base Source"

    def __init__(self, config: SourceConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "MorningByte/0.1.0 (https://github.com/morning-byte)"
            },
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()

    @abstractmethod
    async def fetch(self) -> list[Article]:
        """Fetch articles from the source."""
        pass

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
