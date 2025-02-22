import os
import requests
import logging
from datetime import datetime

def update_render_cookies():
    """Update cookies file on Render.com"""
    try:
        cookie_url = os.environ.get('COOKIE_UPDATE_URL')
        if not cookie_url:
            return False
            
        response = requests.get(cookie_url)
        if response.status_code == 200:
            cookie_file = '/tmp/downloads/cookies.txt'
            with open(cookie_file, 'w') as f:
                f.write(response.text)
            return True
    except Exception as e:
        logging.error(f"Cookie update failed: {e}")
        return False

if __name__ == '__main__':
    update_render_cookies()