import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for Flask application"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Determine if running on Render.com
    IS_RENDER = os.environ.get('RENDER', '').lower() == 'true'
    
    # Application directories
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    if IS_RENDER:
        DOWNLOAD_DIR = '/tmp/downloads'
    else:
        DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
    
    # YouTube Download Settings
    MAX_FILESIZE = int(os.environ.get('MAX_FILESIZE', 1024 * 1024 * 1024))  # 1GB default
    ALLOWED_FORMATS = ['mp4', 'mp3', 'webm']
    MAX_DURATION = int(os.environ.get('MAX_DURATION', 7200))  # 2 hours default
    DOWNLOAD_TIMEOUT = int(os.environ.get('DOWNLOAD_TIMEOUT', 300))  # 5 minutes default
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate limiting
    RATELIMIT_DEFAULT = '30/minute'
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    
    # Error reporting
    PROPAGATE_EXCEPTIONS = True
    
    # Ensure downloads directory exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Debug settings (disable in production)
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # YouTube specific settings
    YOUTUBE_SETTINGS = {
        'geo_bypass': True,
        'geo_bypass_country': os.environ.get('GEO_BYPASS_COUNTRY', 'US'),
        'socket_timeout': int(os.environ.get('SOCKET_TIMEOUT', 30)),
        'retries': int(os.environ.get('DOWNLOAD_RETRIES', 3)),
        'nocheckcertificate': True
    }
    
    @staticmethod
    def init_app(app):
        """Initialize application with config settings"""
        # Ensure required directories exist
        for dir_name in ['videos', 'audio', 'playlists']:
            path = os.path.join(Config.DOWNLOAD_DIR, dir_name)
            os.makedirs(path, exist_ok=True)