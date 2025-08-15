# eKYC News Crawler

An automated RSS feed crawler and aggregator for monitoring developments in eKYC (electronic Know Your Customer) and digital identity verification across multiple academic and industry disciplines.

## Features

- **Multi-source RSS crawling**: Monitors academic, regulatory, industry, and cybersecurity feeds
- **Intelligent relevance scoring**: Filters articles based on eKYC/digital identity keywords
- **Multiple output formats**: JSON, CSV, and HTML reports
- **Automated scheduling**: Daily crawls at configurable times
- **Comprehensive coverage**: Covers computer science, law, finance, cybersecurity, and more
- **Recent article filtering**: Focus on articles from the last N days

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Run a single crawl:
```bash
python cli.py crawl
```

#### Run crawl with custom parameters:
```bash
python cli.py crawl --days 14 --output-dir my_reports
```

#### Start automated scheduler:
```bash
python cli.py schedule
```

#### Test with subset of feeds:
```bash
python cli.py test
```

#### List all configured feeds:
```bash
python cli.py list-feeds
```

### Direct Python Usage

```python
from crawler import EKYCNewsCrawler

crawler = EKYCNewsCrawler()
results = crawler.run_crawl(days_filter=7)

print(f"Found {results['relevant_articles']} relevant articles")
```

## Configuration

Edit `config.py` to customize:

- **RSS_FEEDS**: Add/remove RSS feed sources
- **KEYWORDS**: Modify relevance scoring keywords
- **MAX_ARTICLES_PER_FEED**: Limit articles per feed
- **OUTPUT_DIR**: Change output directory

## Feed Categories

The crawler monitors feeds across these categories:

### Academic
- arXiv Computer Science, Cryptography, Machine Learning
- Academic papers on digital identity research

### RegTech (Regulatory Technology)
- A Team Insight RegTech
- Fintech News Switzerland RegTech
- RegtechTimes
- The Fintech Times RegTech
- TechBullion RegTech
- TheFinanser Regulation
- Encompass RegTech Blog

### Industry
- Risk.net Regulation
- Finextra Risk
- Biometric Update
- Identity Week

### Cybersecurity
- NIST Cybersecurity
- Dark Reading Identity
- Security Week Identity

## Output Files

Each crawl generates three files:

1. **JSON** (`ekyc_news_YYYYMMDD_HHMMSS.json`): Raw structured data
2. **CSV** (`ekyc_news_YYYYMMDD_HHMMSS.csv`): Spreadsheet format
3. **HTML** (`ekyc_news_YYYYMMDD_HHMMSS.html`): Formatted report with relevance scoring

## Relevance Scoring

Articles are scored based on keyword matching:
- **Title matches**: 3 points per keyword
- **Summary matches**: 1 point per keyword

Keywords include: ekyc, digital identity, biometric, kyc, aml, verification, compliance, regtech, blockchain identity, etc.

## Scheduling

The scheduler runs crawls twice daily:
- 9:00 AM
- 5:00 PM

Modify `scheduler.py` to change timing.

## Customization

### Adding New RSS Feeds

Edit `config.py`:

```python
RSS_FEEDS = {
    "Your Category": {
        "Source Name": "https://example.com/feed.xml",
    }
}
```

### Adding Keywords

Edit `config.py`:

```python
KEYWORDS = [
    "your-keyword",
    "another-keyword",
    # ... existing keywords
]
```

## Error Handling

- Graceful handling of unavailable feeds
- Timeout protection for slow feeds
- Logging of all operations
- Continues processing even if individual feeds fail

## Requirements

- Python 3.7+
- Internet connection
- Dependencies listed in `requirements.txt`

## License

For internal use only.
