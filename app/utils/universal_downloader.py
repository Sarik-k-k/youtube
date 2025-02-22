import os
import yt_dlp
import random
import logging
from datetime import datetime
import shutil
from flask import current_app
from .cookie_manager import get_youtube_cookies

logger = logging.getLogger(__name__)

def ensure_directory(path):
    """Ensure directory exists and is writable"""
    try:
        os.makedirs(path, exist_ok=True)
        # Test if directory is writable
        test_file = os.path.join(path, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except Exception as e:
        logger.error(f"Directory creation/write test failed for {path}: {str(e)}")
        return False

def get_safe_filename(filename):
    """Convert filename to safe version"""
    # Remove invalid characters
    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
    # Limit length
    return filename[:200]

def get_rotating_user_agents():
    return [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15'
    ]

def get_download_options(download_type, base_path):
    """Get download options with safe path handling"""
    # Ensure base directories exist
    video_path = os.path.join(base_path, 'videos')
    audio_path = os.path.join(base_path, 'audio')
    
    for path in [video_path, audio_path]:
        if not ensure_directory(path):
            raise RuntimeError(f"Cannot create/write to directory: {path}")

    headers = {
        'User-Agent': random.choice(get_rotating_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers'
    }

    common_opts = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'http_headers': headers,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],  # Try multiple clients
                'player_skip': ['webpage', 'config', 'js'],
                'skip': ['dash', 'hls']
            }
        },
        'socket_timeout': 15,
        'retries': 5,
        'file_access_retries': 3,
        'fragment_retries': 3,
        'retry_sleep_functions': {'http': lambda n: 5 * (n + 1)},
        'ignoreerrors': True,
        'no_color': True,
        'outtmpl': {
            'default': os.path.join(
                base_path, 
                '%(extractor)s', 
                '%(title).200s.%(ext)s'
            )
        },
        'paths': {
            'home': base_path,
            'temp': os.path.join(base_path, 'temp'),
        },
        'writethumbnail': False,
        'progress_hooks': [lambda d: logger.debug(f"Download progress: {d.get('_percent_str', 'N/A')}")],
    }

    type_specific_opts = {
        'video': {
            'format': 'best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(video_path, '%(title).200s.%(ext)s')
        },
        'audio': {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(audio_path, '%(title).200s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }
    }

    return {**common_opts, **type_specific_opts.get(download_type, {})}

def download_youtube_content(url, content_type='video'):
    """Download content from YouTube with enhanced error handling"""
    try:
        config = current_app.config
        ydl_opts = config['YOUTUBE_SETTINGS'].copy()
        
        # Try to get cookies if available
        if not config['IS_RENDER']:
            cookie_file = get_youtube_cookies()
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file
        
        # Add mobile user agent for Render.com
        if config['IS_RENDER']:
            ydl_opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36'
            }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                if info:
                    filename = ydl.prepare_filename(info)
                    return filename
            except Exception as e:
                logger.error(f"Download failed: {e}")
                
                # Fallback to alternative format
                ydl_opts.update({
                    'format': 'worst[ext=mp4]/worst',
                    'force_generic_extractor': True
                })
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
                
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None
