import os
import yt_dlp
import requests
import unicodedata
import re

def sanitize_filename(filename):
    """
    Sanitize filename to remove invalid characters and limit length.
    """
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^\w\-_\. ]', '_', filename)
    max_length = 255
    return filename[:max_length]

def download_thumbnail(url):
    """
    Retrieve the highest quality thumbnail for a given YouTube video URL and return its binary data.
    
    Instead of saving the thumbnail to the server's filesystem, this function returns a tuple
    containing the suggested filename, the binary content, and the content type. Your web endpoint 
    can then stream this content directly to the user's device.
    
    Args:
        url (str): YouTube video URL

    Returns:
        tuple: (filename, thumbnail bytes, content type) if successful, or None on failure.
    """
    ydl_opts = {
        'format': 'best',
        'no_warnings': True,
        'quiet': True,
        'skip_download': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            
            thumbnails = info_dict.get('thumbnails', [])
            best_thumbnail = max(thumbnails, key=lambda x: x.get('height', 0)) if thumbnails else None
            if not best_thumbnail:
                raise ValueError("No thumbnail found")
            
            title = sanitize_filename(info_dict.get('title', 'unknown'))
            ext = best_thumbnail.get('ext', None)
            if not ext:
                parsed = os.path.splitext(best_thumbnail['url'])[1]
                ext = parsed.lstrip('.') if parsed else 'jpg'
            filename = f"{title}_thumbnail.{ext}"
            
            response = requests.get(best_thumbnail['url'])
            response.raise_for_status()
            content = response.content
            content_type = response.headers.get('Content-Type', f"image/{ext}")
            
            return filename, content, content_type
    
    except Exception as e:
        print(f"Thumbnail download error: {e}")
        return None

def get_thumbnail_info(url):
    """
    Retrieve thumbnail information for a YouTube video.
    
    Args:
        url (str): YouTube video URL
    
    Returns:
        dict: Thumbnail information including video title and details of available thumbnails
    """
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            
            thumbnails = info_dict.get('thumbnails', [])
            thumbnail_info = [{
                'height': thumb.get('height', 0),
                'width': thumb.get('width', 0),
                'url': thumb.get('url', ''),
                'resolution': f"{thumb.get('width', 0)}x{thumb.get('height', 0)}"
            } for thumb in thumbnails]
            
            return {
                'video_title': info_dict.get('title', 'Unknown'),
                'thumbnails': thumbnail_info
            }
    
    except Exception as e:
        print(f"Thumbnail info error: {e}")
        return None