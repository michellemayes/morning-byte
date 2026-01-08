"""Main CLI entry point for Morning Byte."""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from morning_byte.config import Config
from morning_byte.delivery import EmailDelivery, LocalDelivery
from morning_byte.epub.generator import EPUBGenerator, create_digest_from_articles
from morning_byte.models import Article
from morning_byte.sources import SOURCES

app = typer.Typer(
    name="morning-byte",
    help="Daily tech news digest delivered as beautiful EPUBs to your Kindle.",
    add_completion=False,
)
console = Console()


async def fetch_all_sources(config: Config) -> dict[str, list[Article]]:
    """Fetch articles from all enabled sources."""
    articles_by_source: dict[str, list[Article]] = {}

    for source_name, source_config in config.sources.items():
        if not source_config.enabled:
            continue

        source_class = SOURCES.get(source_name)
        if not source_class:
            continue

        try:
            async with source_class(source_config) as source:
                articles = await source.fetch()

                # Group by actual source name (e.g., subreddit name)
                for article in articles:
                    source_key = article.source
                    if source_key not in articles_by_source:
                        articles_by_source[source_key] = []
                    articles_by_source[source_key].append(article)

        except Exception as e:
            console.print(f"[yellow]Warning: Failed to fetch from {source_name}: {e}[/yellow]")

    return articles_by_source


@app.command()
def generate(
    config_path: Path = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
    output: Path = typer.Option(
        None, "--output", "-o", help="Output EPUB file path"
    ),
    send: bool = typer.Option(
        False, "--send", "-s", help="Send to Kindle after generation"
    ),
    preview: bool = typer.Option(
        False, "--preview", "-p", help="Show preview without generating"
    ),
):
    """Generate today's tech news digest."""
    config = Config.load(config_path)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Fetch articles
        task = progress.add_task("Fetching articles from sources...", total=None)
        articles_by_source = asyncio.run(fetch_all_sources(config))
        progress.remove_task(task)

        total_articles = sum(len(a) for a in articles_by_source.values())
        console.print(f"[green]✓[/green] Fetched {total_articles} articles from {len(articles_by_source)} sources")

        if preview:
            _show_preview(articles_by_source)
            return

        if total_articles == 0:
            console.print("[yellow]No articles found. Check your configuration.[/yellow]")
            raise typer.Exit(1)

        # Create digest
        task = progress.add_task("Creating digest...", total=None)
        digest = create_digest_from_articles(articles_by_source, config.digest)
        progress.remove_task(task)

        # Generate EPUB
        task = progress.add_task("Generating EPUB...", total=None)
        generator = EPUBGenerator(config.digest)

        if output:
            epub_path = generator.generate(digest, output)
        else:
            # Use temp file, then save to output dir
            with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
                temp_path = Path(f.name)
            epub_path = generator.generate(digest, temp_path)

            # Save locally
            local = LocalDelivery(config.delivery)
            epub_path = local.save(temp_path)
            temp_path.unlink()

            # Cleanup old files
            deleted = local.cleanup_old()
            if deleted:
                console.print(f"[dim]Cleaned up {len(deleted)} old digest(s)[/dim]")

        progress.remove_task(task)
        console.print(f"[green]✓[/green] Generated: {epub_path}")

        # Send to Kindle if requested
        if send:
            task = progress.add_task("Sending to Kindle...", total=None)
            email = EmailDelivery(config.delivery)

            if email.send(epub_path):
                progress.remove_task(task)
                console.print(f"[green]✓[/green] Sent to {config.delivery.kindle_email}")
            else:
                progress.remove_task(task)
                console.print("[red]✗[/red] Failed to send. Check your email configuration.")
                console.print("[dim]Run 'morning-byte setup' for configuration help.[/dim]")


@app.command()
def preview(
    config_path: Path = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
):
    """Preview what articles would be included in today's digest."""
    config = Config.load(config_path)

    with console.status("Fetching articles..."):
        articles_by_source = asyncio.run(fetch_all_sources(config))

    _show_preview(articles_by_source)


def _show_preview(articles_by_source: dict[str, list[Article]]):
    """Display a preview of articles."""
    for source, articles in sorted(articles_by_source.items()):
        if not articles:
            continue

        table = Table(title=f"📰 {source}", show_header=True)
        table.add_column("Score", style="green", width=6)
        table.add_column("Title", style="bold")
        table.add_column("Comments", style="cyan", width=10)

        for article in articles[:10]:
            score = str(article.score) if article.score else "-"
            comments = str(article.comments_count) if article.comments_count else "-"
            title = article.title[:70] + "..." if len(article.title) > 70 else article.title
            table.add_row(score, title, comments)

        console.print(table)
        console.print()


@app.command()
def setup():
    """Interactive setup and configuration help."""
    console.print("\n[bold]Morning Byte Setup[/bold]\n")

    # Show email setup instructions
    console.print(EmailDelivery.get_setup_instructions())

    # Create example config
    console.print("\n[bold]Creating example configuration...[/bold]")
    config = Config.default()
    config_path = Path("config.example.yaml")
    config.save(config_path)
    console.print(f"[green]✓[/green] Created {config_path}")
    console.print("\nCopy this to config.yaml and customize it for your needs.")
    console.print("Then run: [bold]morning-byte generate --send[/bold]")


@app.command()
def sources():
    """List available news sources."""
    table = Table(title="Available Sources")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Auth Required")

    sources_info = [
        ("hackernews", "Hacker News top stories", "No"),
        ("reddit", "Reddit posts from configured subreddits", "No"),
        ("lobsters", "Lobsters computing-focused stories", "No"),
        ("devto", "Dev.to articles by tag", "No"),
        ("rss", "Custom RSS/Atom feeds", "No"),
    ]

    for name, desc, auth in sources_info:
        table.add_row(name, desc, f"[green]{auth}[/green]")

    console.print(table)
    console.print("\n[dim]All sources use free public APIs with no authentication required.[/dim]")


@app.command()
def list_digests(
    config_path: Path = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
):
    """List previously generated digests."""
    config = Config.load(config_path)
    local = LocalDelivery(config.delivery)
    digests = local.list_digests()

    if not digests:
        console.print("[yellow]No digests found.[/yellow]")
        return

    table = Table(title="Generated Digests")
    table.add_column("Date", style="bold")
    table.add_column("File")
    table.add_column("Size")

    for path, date in digests:
        size = f"{path.stat().st_size / 1024:.1f} KB"
        table.add_row(
            date.strftime("%Y-%m-%d"),
            str(path),
            size,
        )

    console.print(table)


@app.command()
def cron():
    """Output cron configuration for daily execution."""
    console.print("\n[bold]Cron Configuration[/bold]\n")
    console.print("Add one of these lines to your crontab (crontab -e):\n")

    console.print("[bold]Daily at 6 AM:[/bold]")
    console.print("0 6 * * * cd /path/to/morning-byte && .venv/bin/morning-byte generate --send")

    console.print("\n[bold]Daily at 6 AM with logging:[/bold]")
    console.print("0 6 * * * cd /path/to/morning-byte && .venv/bin/morning-byte generate --send >> /var/log/morning-byte.log 2>&1")

    console.print("\n[bold]Using systemd timer (recommended):[/bold]")
    console.print("See README.md for systemd timer configuration.\n")


if __name__ == "__main__":
    app()
