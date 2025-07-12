#!/usr/bin/env python3

import feedparser
import sys
from typing import Dict, Tuple


def validate_rss(file_path: str) -> Tuple[bool, Dict]:

    feed = feedparser.parse(file_path)
    if feed.bozo:
        print(f"❌ error: {feed.bozo_exception}")
        return False, None
        
    feed_info = {
        'title': feed.feed.get('title', 'N/A'),
        'description': feed.feed.get('description', 'N/A'),
        'link': feed.feed.get('link', 'N/A'),
        'entries': len(feed.entries)
    }
    
    print("✅ feed is valid!")
    print(f"    - title: {feed_info['title']}")
    print(f"    - description: {feed_info['description']}")
    print(f"    - link: {feed_info['link']}")
    print(f"    - number of entries: {feed_info['entries']}")
    
    return True, feed_info


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python validate_rss.py <rss_file>")
        return 1
    file_path = sys.argv[1]
    is_valid, _ = validate_rss(file_path)
    
    return 0 if is_valid else 1


if __name__ == '__main__':
    sys.exit(main()) 
