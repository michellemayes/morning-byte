# Morning Byte ☕📱

**Daily tech news digest delivered as beautiful EPUBs to your Kindle.**

Morning Byte aggregates the best tech content from Hacker News, Reddit, Lobsters, Dev.to, and your favorite RSS feeds, then packages it into a beautifully formatted EPUB that's automatically delivered to your Kindle each morning.

## Features

- 📰 **Multiple Sources**: Hacker News, Reddit, Lobsters, Dev.to, and custom RSS feeds
- 📚 **Beautiful EPUBs**: Clean, readable formatting optimized for e-readers
- 📧 **Kindle Delivery**: Automatic delivery via Amazon's Send-to-Kindle
- ⚙️ **Configurable**: Choose your sources, subreddits, and topics
- 🆓 **Free APIs**: All sources use free public APIs (no API keys needed)
- ⏰ **Cron-Ready**: Easy to set up for daily automated delivery

## Quick Start

```bash
# Install
pip install -e .

# Generate your first digest
morning-byte generate

# Preview what's included
morning-byte preview

# Set up Kindle delivery
morning-byte setup
```

## Installation

### Using pip

```bash
# Clone the repo
git clone https://github.com/yourusername/morning-byte.git
cd morning-byte

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install
pip install -e .
```

### Using uv (recommended)

```bash
git clone https://github.com/yourusername/morning-byte.git
cd morning-byte
uv sync
```

## Configuration

Create a `config.yaml` file (or run `morning-byte setup` to generate one):

```yaml
sources:
  hackernews:
    enabled: true
    max_items: 15

  reddit:
    enabled: true
    max_items: 10
    subreddits:
      - programming
      - technology
      - MachineLearning
      - LocalLLaMA
      - rust
      - golang

  lobsters:
    enabled: true
    max_items: 10

  devto:
    enabled: true
    max_items: 10
    tags:
      - python
      - javascript
      - ai
      - webdev

  rss:
    enabled: true
    max_items: 5
    feeds:
      - url: https://blog.pragmaticengineer.com/rss/
        name: Pragmatic Engineer
      - url: https://simonwillison.net/atom/everything/
        name: Simon Willison
      - url: https://www.joelonsoftware.com/feed/
        name: Joel on Software

delivery:
  kindle_email: yourname@kindle.com
  sender_email: you@gmail.com
  smtp_host: smtp.gmail.com
  smtp_port: 587
  output_dir: ./output
  keep_days: 7

digest:
  title: Morning Byte
  subtitle: Your Daily Tech Digest
  max_articles_per_section: 15
  include_comments_link: true
  include_scores: true
```

### Environment Variables

Sensitive settings can be set via environment variables:

```bash
export KINDLE_EMAIL="yourname@kindle.com"
export SENDER_EMAIL="you@gmail.com"
export SMTP_USER="you@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

## Kindle Email Setup

1. **Find your Kindle email**:
   - Go to [Amazon](https://amazon.com) → Account → Content & Devices → Preferences
   - Under "Personal Document Settings", find your Kindle email
   - It looks like: `yourname_abc123@kindle.com`

2. **Add approved sender**:
   - In the same settings, add your sender email to "Approved Personal Document E-mail List"

3. **Configure Gmail (recommended)**:
   - Enable 2-factor authentication
   - Go to Google Account → Security → App Passwords
   - Generate an app password for "Mail"
   - Use this app password in your config

## Usage

### Generate a digest

```bash
# Generate and save locally
morning-byte generate

# Generate and send to Kindle
morning-byte generate --send

# Generate with custom config
morning-byte generate --config /path/to/config.yaml

# Generate to specific output file
morning-byte generate --output ~/my-digest.epub
```

### Preview articles

```bash
morning-byte preview
```

### List available sources

```bash
morning-byte sources
```

### View generated digests

```bash
morning-byte list-digests
```

## Automated Daily Delivery

### Using GitHub Actions (Free Cloud Cron - Recommended)

The easiest way to run Morning Byte automatically - completely free!

**Setup (5 minutes):**

1. **Fork/push this repo to GitHub**

2. **Add secrets** in your repo → Settings → Secrets and variables → Actions:
   - `KINDLE_EMAIL` - Your Kindle email (e.g., `yourname_abc@kindle.com`)
   - `SENDER_EMAIL` - Your Gmail address
   - `SMTP_USER` - Your Gmail address
   - `SMTP_PASSWORD` - Gmail app password ([create one here](https://myaccount.google.com/apppasswords))

3. **Customize** `config.yaml` with your preferred subreddits, RSS feeds, etc.

4. **Done!** The workflow runs daily at 6 AM UTC. You can also trigger it manually from Actions tab.

**Cost:** Free for public repos. Private repos get 2000 minutes/month free (this uses ~1 min/day = 30 min/month).

**Test it:** Go to Actions → "Daily Tech Digest" → "Run workflow"

---

### Using cron (self-hosted)

```bash
# Edit crontab
crontab -e

# Add line for daily 6 AM delivery
0 6 * * * cd /path/to/morning-byte && .venv/bin/morning-byte generate --send >> /var/log/morning-byte.log 2>&1
```

### Using systemd (recommended for Linux)

Create `/etc/systemd/system/morning-byte.service`:

```ini
[Unit]
Description=Morning Byte Daily Tech Digest
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=youruser
WorkingDirectory=/path/to/morning-byte
ExecStart=/path/to/morning-byte/.venv/bin/morning-byte generate --send
Environment="KINDLE_EMAIL=yourname@kindle.com"
Environment="SENDER_EMAIL=you@gmail.com"
Environment="SMTP_USER=you@gmail.com"
Environment="SMTP_PASSWORD=your-app-password"

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/morning-byte.timer`:

```ini
[Unit]
Description=Run Morning Byte daily

[Timer]
OnCalendar=*-*-* 06:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable the timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable morning-byte.timer
sudo systemctl start morning-byte.timer
```

## News Sources

| Source | Description | Auth Required |
|--------|-------------|---------------|
| Hacker News | Top stories from HN | No |
| Reddit | Posts from configured subreddits | No |
| Lobsters | Computing-focused stories | No |
| Dev.to | Articles by tag | No |
| RSS | Any RSS/Atom feed | No |

All sources use free public APIs with no authentication required.

## Recommended RSS Feeds

Here are some great tech blogs to add:

```yaml
feeds:
  # Engineering blogs
  - url: https://blog.pragmaticengineer.com/rss/
    name: Pragmatic Engineer
  - url: https://simonwillison.net/atom/everything/
    name: Simon Willison
  - url: https://martinfowler.com/feed.atom
    name: Martin Fowler

  # Company engineering blogs
  - url: https://netflixtechblog.com/feed
    name: Netflix Tech Blog
  - url: https://engineering.fb.com/feed/
    name: Meta Engineering
  - url: https://github.blog/feed/
    name: GitHub Blog

  # AI/ML
  - url: https://lilianweng.github.io/index.xml
    name: Lilian Weng
  - url: https://karpathy.github.io/feed.xml
    name: Andrej Karpathy
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff format .
ruff check --fix .
```

## License

MIT License - see LICENSE file for details.

---

Built with ❤️ for morning reading
