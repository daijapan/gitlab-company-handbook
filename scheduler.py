"""
Scheduler for automated crawling
"""

import schedule
import time
import logging
from datetime import datetime
from crawler import EKYCNewsCrawler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_scheduled_crawl():
    """Run scheduled crawl"""
    logger.info("Starting scheduled crawl...")
    try:
        crawler = EKYCNewsCrawler()
        results = crawler.run_crawl()
        logger.info(f"Scheduled crawl completed. Relevant articles: {results['relevant_articles']}")
    except Exception as e:
        logger.error(f"Scheduled crawl failed: {e}")

def start_scheduler():
    """Start the scheduler"""
    schedule.every().day.at("09:00").do(run_scheduled_crawl)  # Daily at 9 AM
    schedule.every().day.at("17:00").do(run_scheduled_crawl)  # Daily at 5 PM
    
    logger.info("Scheduler started. Crawls scheduled for 9:00 AM and 5:00 PM daily.")
    logger.info("Press Ctrl+C to stop the scheduler.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped.")

if __name__ == "__main__":
    start_scheduler()
