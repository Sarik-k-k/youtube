from flask import Flask
from .config import Config
import logging
import os
from logging.handlers import RotatingFileHandler

def configure_logging(app):
    """Configure logging for the application"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = RotatingFileHandler(
        'logs/youtube_downloader.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('YouTube Downloader startup')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Configure logging
    configure_logging(app)
    
    # Configure custom error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Page not found: {error}')
        return {'error': 'Not Found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return {'error': 'Internal Server Error'}, 500
    
    # Register routes
    from .routes import main
    app.register_blueprint(main)
    
    # Register CLI commands if needed
    @app.cli.command('init-downloads')
    def init_downloads():
        """Initialize download directories."""
        dirs = ['downloads', 'downloads/videos', 'downloads/audio', 'downloads/playlists']
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        app.logger.info('Download directories initialized')
    
    return app