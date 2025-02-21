import os
import yt_dlp
import requests
import unicodedata
import re
import random
import logging
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_rotating_user_agents():
    """Return a list of user agents to rotate through"""
    return [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15'
    ]

def sanitize_filename(filename):
    """Sanitize filename to remove invalid characters and limit length."""
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^\w\-_\. ]', '_', filename)
    return filename[:255]

def get_ydl_opts():
    """Get yt-dlp options with anti-blocking measures"""
    return {
        'format': 'best',
        'no_warnings': True,
        'quiet': True,
        'skip_download': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],
                'player_skip': ['webpage', 'configs']
            }
        },
        'http_headers': {
            'User-Agent': random.choice(get_rotating_user_agents()),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    }

def download_thumbnail(url):
    """
    Retrieve the highest quality thumbnail with improved error handling and anti-blocking measures.
    
    Args:
        url (str): YouTube video URL

    Returns:
        tuple: (filename, thumbnail bytes, content type) if successful, or None on failure.
    """
    logger.info(f"Attempting to download thumbnail for: {url}")
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            
            # Get all thumbnails and sort by quality
            thumbnails = info_dict.get('thumbnails', [])
            if not thumbnails:
                raise ValueError("No thumbnails found")
            
            # Try multiple thumbnail qualities in case some fail
            for thumbnail in sorted(thumbnails, key=lambda x: x.get('height', 0), reverse=True):
                try:
                    thumb_url = thumbnail.get('url')
                    if not thumb_url:
                        continue
                    
                    # Prepare filename
                    title = sanitize_filename(info_dict.get('title', 'unknown'))
                    ext = thumbnail.get('ext', None)
                    if not ext:
                        parsed = urlparse(thumb_url)
                        ext = os.path.splitext(parsed.path)[1].lstrip('.') or 'jpg'
                    filename = f"{title}_thumbnail.{ext}"
                    
                    # Download with retry mechanism
                    for attempt in range(3):
                        try:
                            headers = {
                                'User-Agent': random.choice(get_rotating_user_agents()),
                                'Referer': 'https://www.youtube.com/'
                            }
                            response = requests.get(thumb_url, headers=headers, timeout=10)
                            response.raise_for_status()
                            
                            content = response.content
                            content_type = response.headers.get('Content-Type', f"image/{ext}")
                            
                            logger.info(f"Successfully downloaded thumbnail: {filename}")
                            return filename, content, content_type
                        
                        except requests.RequestException as e:
                            if attempt == 2:  # Last attempt
                                logger.error(f"Failed to download thumbnail after 3 attempts: {e}")
                                continue
                            logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                
                except Exception as e:
                    logger.error(f"Error processing thumbnail: {e}")
                    continue
            
            raise ValueError("All thumbnail download attempts failed")
    
    except Exception as e:
        logger.error(f"Thumbnail download error: {e}")
        
        # Try alternate method with different options
        try:
            alternate_opts = get_ydl_opts()
            alternate_opts.update({
                'force_generic_extractor': True,
                'extract_flat': True
            })
            
            with yt_dlp.YoutubeDL(alternate_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                thumbnail_url = info_dict.get('thumbnail')
                
                if thumbnail_url:
                    headers = {
                        'User-Agent': random.choice(get_rotating_user_agents()),
                        'Referer': 'https://www.youtube.com/'
                    }
                    response = requests.get(thumbnail_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    title = sanitize_filename(info_dict.get('title', 'unknown'))
                    ext = 'jpg'
                    filename = f"{title}_thumbnail.{ext}"
                    
                    logger.info(f"Successfully downloaded thumbnail using alternate method: {filename}")
                    return filename, response.content, 'image/jpeg'
        
        except Exception as e2:
            logger.error(f"Alternate thumbnail download method failed: {e2}")
        
        return None

def get_thumbnail_info(url):
    """Enhanced thumbnail information retrieval with better error handling"""
    logger.info(f"Retrieving thumbnail info for: {url}")
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            
            thumbnails = info_dict.get('thumbnails', [])
            thumbnail_info = [{
                'height': thumb.get('height', 0),
                'width': thumb.get('width', 0),
                'url': thumb.get('url', ''),
                'resolution': f"{thumb.get('width', 0)}x{thumb.get('height', 0)}",
                'format': thumb.get('ext', 'unknown')
            } for thumb in thumbnails]
            
            return {
                'video_title': info_dict.get('title', 'Unknown'),
                'video_id': info_dict.get('id', 'Unknown'),
                'thumbnails': sorted(thumbnail_info, key=lambda x: x['height'], reverse=True)
            }
    
    except Exception as e:
        logger.error(f"Thumbnail info error: {e}")
        return None