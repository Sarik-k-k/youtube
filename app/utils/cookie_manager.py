import os
import logging
import browser_cookie3
from flask import current_app

logger = logging.getLogger(__name__)

def get_youtube_cookies():
    """Extract YouTube cookies from browser"""
    try:
        cookies = browser_cookie3.chrome(domain_name='.youtube.com')
        cookie_file = os.path.join(current_app.config['DOWNLOAD_DIR'], 'cookies.txt')
        
        with open(cookie_file, 'w') as f:
            for cookie in cookies:
                f.write(f'{cookie.domain}\tTRUE\t{cookie.path}\t'
                       f'{"TRUE" if cookie.secure else "FALSE"}\t{cookie.expires}\t'
                       f'{cookie.name}\t{cookie.value}\n')
        
        return cookie_file
    except Exception as e:
        logger.error(f"Failed to extract cookies: {e}")
        return None