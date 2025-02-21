import os
import yt_dlp
import requests
import unicodedata
import re
import random
import logging
from urllib.parse import urlparse
from flask import current_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_rotating_user_agents():
    """Return a list of user agents to rotate through"""
    return [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'
    ]

def get_ydl_opts():
    """Get yt-dlp options with anti-blocking measures"""
    return {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'skip_download': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],
                'player_skip': ['webpage', 'configs', 'js']
            }
        },
        'http_headers': {
            'User-Agent': random.choice(get_rotating_user_agents()),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://www.youtube.com',
            'Referer': 'https://www.youtube.com/'
        }
    }

def download_thumbnail(url):
    """Enhanced thumbnail downloader with multiple fallback methods"""
    logger.info(f"Attempting to download thumbnail for: {url}")
    
    try:
        # First attempt: Using yt-dlp
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError("Could not extract video info")
            
            # Try different thumbnail qualities
            thumbnails = info.get('thumbnails', [])
            thumbnails.sort(key=lambda x: x.get('height', 0), reverse=True)
            
            for thumb in thumbnails:
                thumb_url = thumb.get('url')
                if not thumb_url:
                    continue
                
                try:
                    headers = {
                        'User-Agent': random.choice(get_rotating_user_agents()),
                        'Referer': 'https://www.youtube.com/'
                    }
                    response = requests.get(thumb_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    # Create filename
                    title = info.get('title', 'unknown')
                    title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '.'))
                    ext = thumb.get('ext', None) or urlparse(thumb_url).path.split('.')[-1] or 'jpg'
                    filename = f"{title[:100]}_thumbnail.{ext}"
                    
                    logger.info(f"Successfully downloaded thumbnail: {filename}")
                    return filename, response.content, response.headers.get('Content-Type', f'image/{ext}')
                    
                except requests.RequestException as e:
                    logger.warning(f"Failed to download thumbnail: {e}")
                    continue
            
            # Fallback: Try direct maxresdefault URL
            video_id = info.get('id')
            if video_id:
                fallback_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                response = requests.get(fallback_url, headers={
                    'User-Agent': random.choice(get_rotating_user_agents())
                }, timeout=10)
                
                if response.status_code == 200:
                    filename = f"{video_id}_thumbnail.jpg"
                    return filename, response.content, 'image/jpeg'
    
    except Exception as e:
        logger.error(f"Thumbnail download error: {str(e)}")
    
    return None

def sanitize_filename(filename):
    """Sanitize filename to remove invalid characters"""
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^\w\-_\. ]', '_', filename)
    return filename[:200]