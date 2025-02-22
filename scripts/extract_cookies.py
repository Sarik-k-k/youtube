import os
import browser_cookie3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_youtube_cookies():
    """Extract YouTube cookies from Chrome browser"""
    try:
        # Get project root directory
        root_dir = Path(__file__).parent.parent
        cookie_file = root_dir / 'cookies.txt'
        
        # Extract cookies from Chrome
        cookies = browser_cookie3.chrome(domain_name='.youtube.com')
        
        with open(cookie_file, 'w', encoding='utf-8') as f:
            for cookie in cookies:
                f.write(f'{cookie.domain}\tTRUE\t{cookie.path}\t'
                       f'{"TRUE" if cookie.secure else "FALSE"}\t{cookie.expires}\t'
                       f'{cookie.name}\t{cookie.value}\n')
        
        logger.info(f"Successfully extracted cookies to: {cookie_file}")
        return str(cookie_file)
    except Exception as e:
        logger.error(f"Failed to extract cookies: {e}")
        return None

if __name__ == '__main__':
    extract_youtube_cookies()
