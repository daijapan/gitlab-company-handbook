"""
eKYC News Crawler - Aggregates headlines from RSS feeds related to 
digital identity verification and eKYC across multiple disciplines
"""

import feedparser
import requests
from datetime import datetime, timedelta
import csv
import json
import os
import re
from urllib.parse import urlparse
from typing import Dict, List, Tuple
import time
import logging
from config import RSS_FEEDS, KEYWORDS, OUTPUT_DIR, MAX_ARTICLES_PER_FEED

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EKYCNewsCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
    def calculate_relevance_score(self, title: str, summary: str = "") -> int:
        """Calculate relevance score based on keyword matching"""
        text = f"{title} {summary}".lower()
        score = 0
        
        for keyword in KEYWORDS:
            if keyword.lower() in text:
                if keyword.lower() in title.lower():
                    score += 3  # Higher weight for title matches
                else:
                    score += 1  # Lower weight for summary matches
                    
        return score
    
    def parse_feed(self, url: str, category: str, source_name: str) -> List[Dict]:
        """Parse a single RSS feed and extract articles"""
        articles = []
        
        try:
            logger.info(f"Fetching feed: {source_name}")
            
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                feed_content = response.content
            except Exception as e:
                logger.warning(f"Failed to fetch {source_name} with requests: {e}")
                feed_content = url
            
            feed = feedparser.parse(feed_content)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parsing warning for {source_name}: {feed.bozo_exception}")
            
            entries = feed.entries[:MAX_ARTICLES_PER_FEED]
            
            for entry in entries:
                try:
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    
                    summary = ""
                    if hasattr(entry, 'summary'):
                        summary = entry.summary
                    elif hasattr(entry, 'description'):
                        summary = entry.description
                    
                    if summary:
                        summary = re.sub(r'<[^>]+>', '', summary)
                        summary = summary.strip()[:500]  # Limit length
                    
                    relevance_score = self.calculate_relevance_score(entry.title, summary)
                    
                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'summary': summary,
                        'published': pub_date.isoformat() if pub_date else None,
                        'source': source_name,
                        'category': category,
                        'relevance_score': relevance_score,
                        'crawled_at': datetime.now().isoformat()
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing entry from {source_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to parse feed {source_name}: {e}")
            
        logger.info(f"Extracted {len(articles)} articles from {source_name}")
        return articles
    
    def crawl_all_feeds(self) -> List[Dict]:
        """Crawl all configured RSS feeds"""
        all_articles = []
        
        for category, feeds in RSS_FEEDS.items():
            logger.info(f"Processing category: {category}")
            
            for source_name, url in feeds.items():
                articles = self.parse_feed(url, category, source_name)
                all_articles.extend(articles)
                
                time.sleep(1)
        
        return all_articles
    
    def filter_recent_articles(self, articles: List[Dict], days: int = 7) -> List[Dict]:
        """Filter articles to only include recent ones"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_articles = []
        
        for article in articles:
            if article['published']:
                try:
                    pub_date = datetime.fromisoformat(article['published'].replace('Z', '+00:00'))
                    if pub_date.replace(tzinfo=None) >= cutoff_date:
                        recent_articles.append(article)
                except:
                    recent_articles.append(article)
            else:
                recent_articles.append(article)
        
        return recent_articles
    
    def generate_report(self, articles: List[Dict]) -> str:
        """Generate HTML report from articles"""
        
        articles_sorted = sorted(articles, 
                               key=lambda x: (x['relevance_score'], x['published'] or ''), 
                               reverse=True)
        
        categories = {}
        for article in articles_sorted:
            cat = article['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(article)
        
        html_template = """<!DOCTYPE html>
<html>
<head>
    <title>eKYC & Digital Identity News Digest</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .category {{ background-color: white; margin-bottom: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .category-header {{ background-color: #34495e; color: white; padding: 15px; border-radius: 5px 5px 0 0; }}
        .article {{ padding: 15px; border-bottom: 1px solid #eee; }}
        .article:last-child {{ border-bottom: none; }}
        .article-title {{ font-weight: bold; color: #2c3e50; margin-bottom: 5px; }}
        .article-meta {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 10px; }}
        .article-summary {{ color: #34495e; line-height: 1.4; }}
        .relevance-score {{ background-color: #e74c3c; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; }}
        .high-relevance {{ background-color: #e74c3c; }}
        .medium-relevance {{ background-color: #f39c12; }}
        .low-relevance {{ background-color: #95a5a6; }}
        .stats {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>eKYC & Digital Identity News Digest</h1>
        <p>Generated on: {timestamp}</p>
    </div>
    
    <div class="stats">
        <h3>Summary Statistics</h3>
        <p><strong>Total Articles:</strong> {total_articles}</p>
        <p><strong>High Relevance (Score ≥ 5):</strong> {high_relevance}</p>
        <p><strong>Medium Relevance (Score 2-4):</strong> {medium_relevance}</p>
        <p><strong>Categories Covered:</strong> {categories_count}</p>
    </div>
    
    {categories_html}
</body>
</html>"""
        
        total_articles = len(articles)
        high_relevance = len([a for a in articles if a['relevance_score'] >= 5])
        medium_relevance = len([a for a in articles if 2 <= a['relevance_score'] < 5])
        categories_count = len(categories)
        
        categories_html = ""
        for category, cat_articles in categories.items():
            categories_html += f'<div class="category">'
            categories_html += f'<div class="category-header"><h2>{category} ({len(cat_articles)} articles)</h2></div>'
            
            for article in cat_articles:
                relevance_class = "high-relevance" if article['relevance_score'] >= 5 else \
                                "medium-relevance" if article['relevance_score'] >= 2 else "low-relevance"
                
                pub_date = "Unknown date"
                if article['published']:
                    try:
                        pub_date = datetime.fromisoformat(article['published'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                    except:
                        pub_date = article['published']
                
                categories_html += f'''
                <div class="article">
                    <div class="article-title">
                        <a href="{article['link']}" target="_blank">{article['title']}</a>
                        <span class="relevance-score {relevance_class}">Score: {article['relevance_score']}</span>
                    </div>
                    <div class="article-meta">
                        <strong>Source:</strong> {article['source']} | 
                        <strong>Published:</strong> {pub_date}
                    </div>
                    <div class="article-summary">{article['summary'][:300]}{'...' if len(article['summary']) > 300 else ''}</div>
                </div>
                '''
            
            categories_html += '</div>'
        
        return html_template.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            total_articles=total_articles,
            high_relevance=high_relevance,
            medium_relevance=medium_relevance,
            categories_count=categories_count,
            categories_html=categories_html
        )
    
    def save_results(self, articles: List[Dict], filename_prefix: str = "ekyc_news"):
        """Save results in multiple formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        json_file = f"{OUTPUT_DIR}/{filename_prefix}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        if articles:
            csv_file = f"{OUTPUT_DIR}/{filename_prefix}_{timestamp}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if articles:
                    fieldnames = articles[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(articles)
        
        html_content = self.generate_report(articles)
        html_file = f"{OUTPUT_DIR}/{filename_prefix}_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Results saved:")
        logger.info(f"  JSON: {json_file}")
        logger.info(f"  CSV: {csv_file}")
        logger.info(f"  HTML: {html_file}")
        
        return {
            'json': json_file,
            'csv': csv_file,
            'html': html_file
        }
    
    def run_crawl(self, days_filter: int = 7) -> Dict:
        """Run the complete crawling process"""
        logger.info("Starting eKYC news crawl...")
        
        all_articles = self.crawl_all_feeds()
        logger.info(f"Total articles crawled: {len(all_articles)}")
        
        recent_articles = self.filter_recent_articles(all_articles, days_filter)
        logger.info(f"Recent articles (last {days_filter} days): {len(recent_articles)}")
        
        relevant_articles = [a for a in recent_articles if a['relevance_score'] > 0]
        logger.info(f"Relevant articles: {len(relevant_articles)}")
        
        file_paths = self.save_results(relevant_articles)
        
        return {
            'total_crawled': len(all_articles),
            'recent_articles': len(recent_articles),
            'relevant_articles': len(relevant_articles),
            'files': file_paths
        }

if __name__ == "__main__":
    crawler = EKYCNewsCrawler()
    results = crawler.run_crawl()
    
    print(f"\n=== Crawl Complete ===")
    print(f"Total articles crawled: {results['total_crawled']}")
    print(f"Recent articles: {results['recent_articles']}")
    print(f"Relevant articles: {results['relevant_articles']}")
    print(f"\nFiles generated:")
    for format_type, file_path in results['files'].items():
        print(f"  {format_type.upper()}: {file_path}")
