"""Configuration management for Morning Byte."""

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class SourceConfig:
    """Configuration for a news source."""

    enabled: bool = True
    max_items: int = 10
    subreddits: list[str] = field(default_factory=list)  # Reddit specific
    feeds: list[dict] = field(default_factory=list)  # RSS specific
    tags: list[str] = field(default_factory=list)  # Dev.to specific


@dataclass
class DeliveryConfig:
    """Configuration for delivery methods."""

    # Email delivery (Send-to-Kindle)
    kindle_email: str = ""
    sender_email: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""  # Use app password for Gmail

    # Local save
    output_dir: str = "./output"
    keep_days: int = 7  # How many days of digests to keep


@dataclass
class DigestConfig:
    """Configuration for the digest content."""

    title: str = "Morning Byte"
    subtitle: str = "Your Daily Tech Digest"
    max_articles_per_section: int = 15
    include_comments_link: bool = True
    include_scores: bool = True
    topics: list[str] = field(default_factory=lambda: ["programming", "ai", "startups", "tech"])


@dataclass
class Config:
    """Main configuration."""

    sources: dict[str, SourceConfig] = field(default_factory=dict)
    delivery: DeliveryConfig = field(default_factory=DeliveryConfig)
    digest: DigestConfig = field(default_factory=DigestConfig)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Config":
        """Load configuration from YAML file."""
        if path is None:
            # Look for config in standard locations
            search_paths = [
                Path("config.yaml"),
                Path("config.yml"),
                Path.home() / ".config" / "morning-byte" / "config.yaml",
                Path("/etc/morning-byte/config.yaml"),
            ]
            for p in search_paths:
                if p.exists():
                    path = p
                    break

        if path is None or not Path(path).exists():
            return cls.default()

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create config from dictionary."""
        sources = {}
        for name, src_data in data.get("sources", {}).items():
            sources[name] = SourceConfig(**src_data) if isinstance(src_data, dict) else SourceConfig()

        delivery_data = data.get("delivery", {})
        # Override with environment variables
        delivery_data.setdefault("kindle_email", os.getenv("KINDLE_EMAIL", ""))
        delivery_data.setdefault("sender_email", os.getenv("SENDER_EMAIL", ""))
        delivery_data.setdefault("smtp_host", os.getenv("SMTP_HOST", "smtp.gmail.com"))
        delivery_data.setdefault("smtp_port", int(os.getenv("SMTP_PORT", "587")))
        delivery_data.setdefault("smtp_user", os.getenv("SMTP_USER", ""))
        delivery_data.setdefault("smtp_password", os.getenv("SMTP_PASSWORD", ""))

        delivery = DeliveryConfig(**delivery_data)
        digest = DigestConfig(**data.get("digest", {}))

        return cls(sources=sources, delivery=delivery, digest=digest)

    @classmethod
    def default(cls) -> "Config":
        """Create default configuration with all sources enabled."""
        sources = {
            "hackernews": SourceConfig(enabled=True, max_items=15),
            "reddit": SourceConfig(
                enabled=True,
                max_items=10,
                subreddits=["programming", "technology", "MachineLearning", "LocalLLaMA"],
            ),
            "lobsters": SourceConfig(enabled=True, max_items=10),
            "devto": SourceConfig(enabled=True, max_items=10, tags=["python", "javascript", "ai"]),
            "rss": SourceConfig(
                enabled=True,
                max_items=5,
                feeds=[
                    {"url": "https://blog.pragmaticengineer.com/rss/", "name": "Pragmatic Engineer"},
                    {"url": "https://simonwillison.net/atom/everything/", "name": "Simon Willison"},
                    {"url": "https://www.joelonsoftware.com/feed/", "name": "Joel on Software"},
                ],
            ),
        }
        return cls(sources=sources)

    def save(self, path: str | Path) -> None:
        """Save configuration to YAML file."""
        data = {
            "sources": {
                name: {
                    "enabled": src.enabled,
                    "max_items": src.max_items,
                    **({"subreddits": src.subreddits} if src.subreddits else {}),
                    **({"feeds": src.feeds} if src.feeds else {}),
                    **({"tags": src.tags} if src.tags else {}),
                }
                for name, src in self.sources.items()
            },
            "delivery": {
                "kindle_email": self.delivery.kindle_email,
                "sender_email": self.delivery.sender_email,
                "smtp_host": self.delivery.smtp_host,
                "smtp_port": self.delivery.smtp_port,
                "output_dir": self.delivery.output_dir,
                "keep_days": self.delivery.keep_days,
            },
            "digest": {
                "title": self.digest.title,
                "subtitle": self.digest.subtitle,
                "max_articles_per_section": self.digest.max_articles_per_section,
                "include_comments_link": self.digest.include_comments_link,
                "include_scores": self.digest.include_scores,
                "topics": self.digest.topics,
            },
        }
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
