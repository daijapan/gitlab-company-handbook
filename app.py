"""
Flask web application for eKYC News Crawler
Provides a web interface to run crawls and view results
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import json
import glob
from datetime import datetime
from crawler import EKYCNewsCrawler
import threading
import time

app = Flask(__name__)

crawl_status = {
    'running': False,
    'last_run': None,
    'results': None,
    'error': None
}

@app.route('/')
def index():
    """Main dashboard showing recent crawl results"""
    html_files = glob.glob('output/ekyc_news_*.html')
    if html_files:
        latest_html = max(html_files, key=os.path.getctime)
        with open(latest_html, 'r', encoding='utf-8') as f:
            report_content = f.read()
    else:
        report_content = None
    
    return render_template('index.html', 
                         report_content=report_content,
                         crawl_status=crawl_status)

@app.route('/crawl', methods=['POST'])
def run_crawl():
    """Start a new crawl"""
    if crawl_status['running']:
        return jsonify({'error': 'Crawl already running'}), 400
    
    days = request.json.get('days', 7) if request.is_json else int(request.form.get('days', 7))
    
    def crawl_thread():
        global crawl_status
        crawl_status['running'] = True
        crawl_status['error'] = None
        
        try:
            crawler = EKYCNewsCrawler()
            results = crawler.run_crawl(days_filter=days)
            crawl_status['results'] = results
            crawl_status['last_run'] = datetime.now().isoformat()
        except Exception as e:
            crawl_status['error'] = str(e)
        finally:
            crawl_status['running'] = False
    
    thread = threading.Thread(target=crawl_thread)
    thread.start()
    
    return jsonify({'message': 'Crawl started', 'status': 'running'})

@app.route('/status')
def get_status():
    """Get current crawl status"""
    return jsonify(crawl_status)

@app.route('/reports')
def list_reports():
    """List all available reports"""
    reports = []
    
    json_files = glob.glob('output/ekyc_news_*.json')
    html_files = glob.glob('output/ekyc_news_*.html')
    csv_files = glob.glob('output/ekyc_news_*.csv')
    
    timestamps = set()
    for f in json_files + html_files + csv_files:
        basename = os.path.basename(f)
        timestamp = basename.split('_')[2] + '_' + basename.split('_')[3].split('.')[0]
        timestamps.add(timestamp)
    
    for timestamp in sorted(timestamps, reverse=True):
        report = {
            'timestamp': timestamp,
            'datetime': datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S'),
            'json': f'output/ekyc_news_{timestamp}.json' if os.path.exists(f'output/ekyc_news_{timestamp}.json') else None,
            'html': f'output/ekyc_news_{timestamp}.html' if os.path.exists(f'output/ekyc_news_{timestamp}.html') else None,
            'csv': f'output/ekyc_news_{timestamp}.csv' if os.path.exists(f'output/ekyc_news_{timestamp}.csv') else None,
        }
        reports.append(report)
    
    return render_template('reports.html', reports=reports)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download a report file"""
    if not filename.startswith('output/ekyc_news_'):
        return "Invalid file", 404
    
    if not os.path.exists(filename):
        return "File not found", 404
    
    return send_file(filename, as_attachment=True)

@app.route('/view/<path:filename>')
def view_html_report(filename):
    """View HTML report in browser"""
    if not filename.startswith('output/ekyc_news_') or not filename.endswith('.html'):
        return "Invalid file", 404
    
    if not os.path.exists(filename):
        return "File not found", 404
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content

@app.route('/feeds')
def list_feeds():
    """List all configured RSS feeds"""
    from config import RSS_FEEDS
    return render_template('feeds.html', feeds=RSS_FEEDS)

if __name__ == '__main__':
    os.makedirs('output', exist_ok=True)
    app.run(host='0.0.0.0', port=8000, debug=True)
