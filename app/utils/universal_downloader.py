import os
import yt_dlp
import unicodedata
import re
import random
import logging

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
    return filename[:255]  # Windows max filename length

def get_download_options(download_type, base_path):
    """Get download options based on content type"""
    common_opts = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'http_headers': {
            'User-Agent': random.choice(get_rotating_user_agents()),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        },
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],
                'player_skip': ['webpage', 'configs']
            }
        },
        'socket_timeout': 10,
        'retries': 3,
        'file_access_retries': 3,
        'fragment_retries': 3,
        'restrictfilenames': True,
        'nooverwrites': True,
        'no_color': True,
        'progress_hooks': [print_progress]
    }

    type_specific_opts = {
        'video': {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(base_path, 'videos', '%(title)s.%(ext)s')
        },
        'audio': {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
            'outtmpl': os.path.join(base_path, 'audio', '%(title)s.%(ext)s')
        },
        'playlist': {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(base_path, 'playlists', '%(playlist_title)s', '%(title)s.%(ext)s'),
            'yes_playlist': True,
            'playlist_items': '1-50'  # Limit to first 50 items
        }
    }

    return {**common_opts, **type_specific_opts.get(download_type, {})}

def download_youtube_content(url, download_type='video'):
    """
    Universal downloader for YouTube content with fallback mechanisms.
    
    Args:
        url (str): YouTube URL
        download_type (str): 'video', 'audio', or 'playlist'
    
    Returns:
        str: Path to downloaded content
    """
    # Use /tmp for Render.com, local directory for development
    base_path = '/tmp/downloads' if os.environ.get('RENDER') else 'downloads'
    
    # Ensure directories exist
    for dir_type in ['videos', 'audio', 'playlists']:
        os.makedirs(os.path.join(base_path, dir_type), exist_ok=True)

    try:
        ydl_opts = get_download_options(download_type, base_path)
        logger.info(f"Attempting download: {url} as {download_type}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if 'entries' in info:  # Playlist
                download_path = os.path.join(base_path, 'playlists', 
                                           sanitize_filename(info.get('playlist_title', 'Unnamed Playlist')))
            else:  # Single video/audio
                download_path = ydl.prepare_filename(info)
                if download_type == 'audio':
                    download_path = os.path.splitext(download_path)[0] + '.mp3'

            if os.path.exists(download_path):
                logger.info(f"Download successful: {download_path}")
                return download_path
            
            raise FileNotFoundError(f"File not found after download: {download_path}")

    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        # Try alternate method with different options
        try:
            alternate_opts = get_download_options(download_type, base_path)
            alternate_opts.update({
                'format': 'worst',  # Try lowest quality as fallback
                'force_generic_extractor': True
            })
            
            with yt_dlp.YoutubeDL(alternate_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                download_path = ydl.prepare_filename(info)
                
                if os.path.exists(download_path):
                    logger.info(f"Alternate download successful: {download_path}")
                    return download_path
                
        except Exception as e2:
            logger.error(f"Alternate download failed: {str(e2)}")
        
        return None

def print_progress(d):
    """Progress tracking hook with improved logging"""
    if d['status'] == 'finished':
        logger.info('Download completed successfully')
    elif d['status'] == 'downloading':
        try:
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            logger.info(f'Download progress: {percent} at {speed}')
        except Exception:
            pass