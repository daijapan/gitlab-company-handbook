"""
Command Line Interface for eKYC News Crawler
"""

import click
from crawler import EKYCNewsCrawler
from scheduler import start_scheduler
import os

@click.group()
def cli():
    """eKYC News Crawler - Aggregate headlines from RSS feeds related to digital identity verification"""
    pass

@cli.command()
@click.option('--days', default=7, help='Number of days to look back for articles (default: 7)')
@click.option('--output-dir', default='output', help='Output directory for results')
def crawl(days, output_dir):
    """Run a single crawl operation"""
    click.echo(f"Starting eKYC news crawl (last {days} days)...")
    
    if output_dir != 'output':
        import config
        config.OUTPUT_DIR = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    crawler = EKYCNewsCrawler()
    results = crawler.run_crawl(days_filter=days)
    
    click.echo(f"\n=== Crawl Results ===")
    click.echo(f"Total articles crawled: {results['total_crawled']}")
    click.echo(f"Recent articles: {results['recent_articles']}")
    click.echo(f"Relevant articles: {results['relevant_articles']}")
    click.echo(f"\nFiles generated:")
    for format_type, file_path in results['files'].items():
        click.echo(f"  {format_type.upper()}: {file_path}")
    
    if 'html' in results['files']:
        html_path = os.path.abspath(results['files']['html'])
        click.echo(f"\nHTML report available at: file://{html_path}")

@cli.command()
def schedule():
    """Start the automated scheduler (runs crawls at 9 AM and 5 PM daily)"""
    click.echo("Starting automated scheduler...")
    start_scheduler()

@cli.command()
def test():
    """Test the crawler with a small subset of feeds"""
    click.echo("Running test crawl...")
    
    import config
    original_feeds = config.RSS_FEEDS.copy()
    
    config.RSS_FEEDS = {
        "Academic": {
            "arXiv Cryptography": "https://rss.arxiv.org/rss/cs.CR",
        },
        "RegTech": {
            "RegtechTimes": "https://regtechtimes.com/feed/",
        }
    }
    
    try:
        crawler = EKYCNewsCrawler()
        results = crawler.run_crawl(days_filter=30)  # Look back 30 days for testing
        
        click.echo(f"\n=== Test Results ===")
        click.echo(f"Total articles crawled: {results['total_crawled']}")
        click.echo(f"Recent articles: {results['recent_articles']}")
        click.echo(f"Relevant articles: {results['relevant_articles']}")
        
    finally:
        config.RSS_FEEDS = original_feeds

@cli.command()
def list_feeds():
    """List all configured RSS feeds"""
    from config import RSS_FEEDS
    
    click.echo("Configured RSS Feeds:")
    click.echo("=" * 50)
    
    for category, feeds in RSS_FEEDS.items():
        click.echo(f"\n{category}:")
        for name, url in feeds.items():
            click.echo(f"  • {name}")
            click.echo(f"    {url}")

if __name__ == '__main__':
    cli()
