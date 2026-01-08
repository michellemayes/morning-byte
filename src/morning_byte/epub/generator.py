"""EPUB generator for Morning Byte."""

from datetime import datetime
from pathlib import Path

from ebooklib import epub
from jinja2 import Template

from morning_byte.config import DigestConfig
from morning_byte.models import Article, Digest, Section

from .styles import EPUB_CSS


class EPUBGenerator:
    """Generate beautiful EPUB files from a digest."""

    def __init__(self, config: DigestConfig):
        self.config = config

    def generate(self, digest: Digest, output_path: str | Path) -> Path:
        """Generate an EPUB file from the digest."""
        book = epub.EpubBook()

        # Set metadata
        book.set_identifier(f"morning-byte-{digest.date.strftime('%Y%m%d')}")
        book.set_title(f"{digest.title} - {digest.date.strftime('%B %d, %Y')}")
        book.set_language("en")
        book.add_author("Morning Byte")

        # Add CSS
        css = epub.EpubItem(
            uid="style",
            file_name="style/main.css",
            media_type="text/css",
            content=EPUB_CSS,
        )
        book.add_item(css)

        # Create chapters
        chapters = []

        # Cover page
        cover = self._create_cover(digest)
        book.add_item(cover)
        chapters.append(cover)

        # Table of contents page
        toc_page = self._create_toc_page(digest)
        book.add_item(toc_page)
        chapters.append(toc_page)

        # Section chapters
        for i, section in enumerate(digest.sections):
            if not section.articles:
                continue

            chapter = self._create_section_chapter(section, i)
            book.add_item(chapter)
            chapters.append(chapter)

        # Define Table of Contents
        book.toc = [epub.Link(ch.file_name, ch.title, ch.id) for ch in chapters]

        # Add navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Define spine
        book.spine = ["nav"] + chapters

        # Write the EPUB file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        epub.write_epub(str(output_path), book)

        return output_path

    def _create_cover(self, digest: Digest) -> epub.EpubHtml:
        """Create the cover page."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <link rel="stylesheet" href="style/main.css" type="text/css" />
</head>
<body>
    <div class="cover">
        <h1>{{ title }}</h1>
        <p class="subtitle">{{ subtitle }}</p>
        <p class="date">{{ date }}</p>
        {% if intro %}
        <p>{{ intro }}</p>
        {% endif %}
        <p class="stats">{{ total_articles }} articles from {{ num_sources }} sources</p>
    </div>
</body>
</html>
""")

        sources = set()
        for section in digest.sections:
            for article in section.articles:
                sources.add(article.source)

        content = template.render(
            title=digest.title,
            subtitle=self.config.subtitle,
            date=digest.date.strftime("%A, %B %d, %Y"),
            intro=digest.intro,
            total_articles=digest.total_articles,
            num_sources=len(sources),
        )

        cover = epub.EpubHtml(title="Cover", file_name="cover.xhtml", lang="en")
        cover.content = content
        cover.add_item(epub.EpubItem(uid="style", file_name="style/main.css", media_type="text/css"))
        return cover

    def _create_toc_page(self, digest: Digest) -> epub.EpubHtml:
        """Create a table of contents page."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>Contents</title>
    <link rel="stylesheet" href="style/main.css" type="text/css" />
</head>
<body>
    <div class="toc">
        <h2>Today's Digest</h2>
        <ul>
        {% for section in sections %}
            {% if section.articles %}
            <li>
                <a href="section_{{ loop.index0 }}.xhtml">{{ section.title }}</a>
                <span class="count">({{ section.articles|length }} articles)</span>
            </li>
            {% endif %}
        {% endfor %}
        </ul>
    </div>
</body>
</html>
""")

        content = template.render(sections=digest.sections)

        toc = epub.EpubHtml(title="Contents", file_name="toc.xhtml", lang="en")
        toc.content = content
        return toc

    def _create_section_chapter(self, section: Section, index: int) -> epub.EpubHtml:
        """Create a chapter for a section."""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>{{ section.title }}</title>
    <link rel="stylesheet" href="style/main.css" type="text/css" />
</head>
<body>
    <div class="section">
        <h2>{{ section.title }}</h2>
        {% if section.description %}
        <p class="section-description">{{ section.description }}</p>
        {% endif %}

        {% for article in articles %}
        <div class="article">
            <h3 class="article-title">
                <a href="{{ article.url }}">{{ article.title }}</a>
            </h3>

            <p class="article-meta">
                <span class="source">{{ article.source }}</span>
                {% if article.author %} · by {{ article.author }}{% endif %}
                {% if include_scores and article.score %}
                 · <span class="score">▲ {{ article.score }}</span>
                {% endif %}
                {% if article.comments_count %}
                 · <a href="{{ article.comments_url }}" class="comments">{{ article.comments_count }} comments</a>
                {% endif %}
            </p>

            {% if article.domain %}
            <p class="article-domain">({{ article.domain }})</p>
            {% endif %}

            {% if article.summary %}
            <p class="article-summary">{{ article.summary }}</p>
            {% endif %}

            {% if article.tags %}
            <div class="tags">
                {% for tag in article.tags[:5] %}
                <span class="tag">{{ tag }}</span>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
""")

        # Limit articles per section
        articles = section.articles[: self.config.max_articles_per_section]

        content = template.render(
            section=section,
            articles=articles,
            include_scores=self.config.include_scores,
            include_comments=self.config.include_comments_link,
        )

        chapter = epub.EpubHtml(
            title=section.title,
            file_name=f"section_{index}.xhtml",
            lang="en",
        )
        chapter.content = content
        return chapter


def create_digest_from_articles(
    articles_by_source: dict[str, list[Article]],
    config: DigestConfig,
) -> Digest:
    """Create a Digest from categorized articles."""
    now = datetime.now()

    sections = []

    # Create a section for each source that has articles
    source_order = ["Hacker News", "Lobsters", "Dev.to"]  # Priority sources first

    # Add priority sources first
    for source_name in source_order:
        if source_name in articles_by_source and articles_by_source[source_name]:
            sections.append(
                Section(
                    title=source_name,
                    articles=articles_by_source[source_name],
                )
            )

    # Add remaining sources (Reddit subreddits, RSS feeds)
    for source_name, articles in articles_by_source.items():
        if source_name not in source_order and articles:
            sections.append(
                Section(
                    title=source_name,
                    articles=articles,
                )
            )

    return Digest(
        title=config.title,
        date=now,
        sections=sections,
        intro=f"Your curated tech digest for {now.strftime('%A, %B %d')}.",
    )
