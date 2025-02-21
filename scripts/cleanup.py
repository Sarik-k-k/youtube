import os
import shutil
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def cleanup_downloads():
    """Clean up old downloads"""
    try:
        download_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'downloads')
        if os.path.exists(download_dir):
            # Remove files older than 24 hours
            cutoff = datetime.now() - timedelta(minutes=2)
            
            for root, dirs, files in os.walk(download_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if datetime.fromtimestamp(os.path.getctime(file_path)) < cutoff:
                        os.remove(file_path)
                        logger.info(f"Removed old file: {file_path}")
                        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")

if __name__ == '__main__':
    cleanup_downloads()