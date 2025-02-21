import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for Flask application"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Determine if running on Render.com
    IS_RENDER = os.environ.get('RENDER', '').lower() == 'true'
    
    # Application directories - Updated path handling
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
    
    # Set download directory based on environment
    if IS_RENDER:
        DOWNLOAD_DIR = '/tmp/downloads'
    else:
        DOWNLOAD_DIR = os.path.join(ROOT_DIR, 'downloads')
    
    # Define download paths with proper directory structure
    DOWNLOAD_PATHS = {
        'base': DOWNLOAD_DIR,
        'video': os.path.join(DOWNLOAD_DIR, 'videos'),
        'audio': os.path.join(DOWNLOAD_DIR, 'audio'),
        'temp': os.path.join(DOWNLOAD_DIR, 'temp'),
        'playlists': os.path.join(DOWNLOAD_DIR, 'playlists')
    }
    
    # YouTube specific settings with enhanced configuration
    YOUTUBE_SETTINGS = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'geo_bypass': True,
        'geo_bypass_country': os.environ.get('GEO_BYPASS_COUNTRY', 'US'),
        'socket_timeout': int(os.environ.get('SOCKET_TIMEOUT', 30)),
        'retries': int(os.environ.get('DOWNLOAD_RETRIES', 3)),
        'fragment_retries': 10,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'paths': DOWNLOAD_PATHS,
        'outtmpl': {
            'default': os.path.join(DOWNLOAD_PATHS['video'], '%(title)s.%(ext)s'),
            'audio': os.path.join(DOWNLOAD_PATHS['audio'], '%(title)s.%(ext)s')
        },
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }],
        'extract_flat': 'in_playlist',
        'concurrent_fragment_downloads': 3
    }
    
    # Download constraints
    MAX_FILESIZE = int(os.environ.get('MAX_FILESIZE', 1024 * 1024 * 1024))
    ALLOWED_FORMATS = ['mp4', 'mp3', 'webm']
    MAX_DURATION = int(os.environ.get('MAX_DURATION', 7200))
    DOWNLOAD_TIMEOUT = int(os.environ.get('DOWNLOAD_TIMEOUT', 300))
    
    # Other settings remain the same
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    RATELIMIT_DEFAULT = '30/minute'
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    PROPAGATE_EXCEPTIONS = True
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')

    @staticmethod
    def init_app(app):
        """Initialize application with config settings"""
        logger = logging.getLogger(__name__)
        
        # Create all required directories with absolute paths
        for name, dir_path in Config.DOWNLOAD_PATHS.items():
            try:
                os.makedirs(dir_path, exist_ok=True)
                # Test write permissions
                test_file = os.path.join(dir_path, '.write_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                logger.info(f'Created directory {name}: {dir_path}')
            except Exception as e:
                logger.error(f'Failed to create/verify directory {dir_path}: {str(e)}')
                raise RuntimeError(f'Cannot create/access directory: {dir_path}')