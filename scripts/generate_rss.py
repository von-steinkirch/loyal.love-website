#!/usr/bin/env python3

import os
import re
from datetime import datetime, UTC
from typing import Dict, List
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


########################################################
#       constants
########################################################

RSS_CONFIG: Dict[str, str] = {
    'title': "bt3gl's lololo",
    'description': "bt3gl's loyal.love.lore",
    'link': "https://loyal.love",
    'ttl': '60'
}

MONTH_MAP: Dict[str, str] = {
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'may': '05', 'june': '06', 'july': '07', 'august': '08',
    'september': '09', 'october': '10', 'november': '11', 'december': '12'
}

CHAPTERS_DIR: str = 'chapters'
INDEX_FILE: str = 'index.html'
RSS_OUTPUT_FILE: str = 'rss.xml'


########################################################
#       public methods
########################################################

def sanitize_text(text: str) -> str:

    replacements = {
        "…": "...", "—": "-", "❤️‍🔥": "*heart*", "🍿": "*popcorn*",
        "🌚": "*moon*", "😀": "*smile*", "🪐": "*planet*", "😼": "*cat*",
        "🙄": "*roll*", "🚬": "*smoke*", "⽊": "*tree*", "<3": "*heart*",
        "∞": "infinity", "→": "->", "^": "^", "%": "percent"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
        

    return ''.join(char for char in text if ord(char) < 128)


def extract_post_data(html_content: str, chapter_name: str = '') -> List[Dict[str, str]]:

    soup = BeautifulSoup(html_content, 'html.parser')
    posts = []
    
    for section in soup.find_all('hr', class_='between-posts'):
        post_id = section.get('id')
        if not post_id:
            continue

        title_elem = section.find_next('h2', class_='post-title')
        text_elem = title_elem and title_elem.find_next('h4', class_='post-text')
        
        if not (title_elem and text_elem):
            continue
            
        title = title_elem.get_text(strip=True)
        text = text_elem.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)

        first_image = None
        for img in section.find_all_next('img', limit=1):
            if img.get('src'):
                first_image = img['src']
                break

        date_match = re.search(r'(\d{4}),\s*(\w+),\s*(\d+)', title)
        if date_match:
            year, month, day = date_match.groups()
            month_num = MONTH_MAP.get(month.lower(), '01')
            naive_date = datetime.strptime(f"{year}-{month_num}-{day.zfill(2)}T00:00:00Z", '%Y-%m-%dT%H:%M:%SZ')
            pub_date = naive_date.replace(tzinfo=UTC)
            
            link = f"{RSS_CONFIG['link']}/chapters/{chapter_name}#{post_id}" if chapter_name else f"{RSS_CONFIG['link']}#{post_id}"
            
            posts.append({
                'title': title,
                'description': text,
                'link': link,
                'guid': link,
                'pubDate': pub_date,
                'image': first_image
            })
    
    return posts


def generate_rss() -> None:

    current_time = datetime.now(UTC)
    all_posts = []

    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                posts = extract_post_data(f.read())
                all_posts.extend(posts)
        except Exception as e:
            print(f"❌  error processing {INDEX_FILE}: {e}")

    try:
        for filename in os.listdir(CHAPTERS_DIR):
            if filename.endswith('.html'):
                file_path = os.path.join(CHAPTERS_DIR, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        posts = extract_post_data(f.read(), filename)
                        all_posts.extend(posts)
                except Exception as e:
                    print(f"❌ error processing {file_path}: {e}")
    except Exception as e:
        print(f"❌ error accessing {CHAPTERS_DIR}: {e}")
    
    all_posts.sort(key=lambda x: x['pubDate'], reverse=True)
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
    rss.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = sanitize_text(RSS_CONFIG['title'])
    ET.SubElement(channel, "description").text = sanitize_text(RSS_CONFIG['description'])
    ET.SubElement(channel, "link").text = RSS_CONFIG['link']
    ET.SubElement(channel, "language").text = "en"
    ET.SubElement(channel, "generator").text = "bt3gl's RSS generator"
    ET.SubElement(channel, "lastBuildDate").text = current_time.strftime("%a, %d %b %Y %H:%M:%S %z")
    ET.SubElement(channel, "pubDate").text = current_time.strftime("%a, %d %b %Y %H:%M:%S %z")
    ET.SubElement(channel, "ttl").text = RSS_CONFIG['ttl']
    atom_link = ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", f"{RSS_CONFIG['link']}/rss.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")
    
    for post in all_posts:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = sanitize_text(post['title'])

        description = post['description']
        if post['image']:
            description += f'<br/><img src="{post["image"]}" alt="Post image"/>'
        ET.SubElement(item, "description").text = description
        ET.SubElement(item, "link").text = post['link']
        guid = ET.SubElement(item, "guid")
        guid.text = post['guid']
        guid.set("isPermaLink", "true")
        ET.SubElement(item, "pubDate").text = post['pubDate'].strftime("%a, %d %b %Y %H:%M:%S %z")

    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str += ET.tostring(rss, encoding='unicode')

    try:
        with open(RSS_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        print(f"✅ successfully generated RSS feed: {RSS_OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ error writing {RSS_OUTPUT_FILE}: {e}")


if __name__ == '__main__':
    generate_rss()
