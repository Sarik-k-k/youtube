from flask import Flask
from .config import Config
from .utils.error_handlers import register_error_handlers
import logging
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        file_handler = logging.FileHandler('logs/youtube_downloader.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('YouTube Downloader startup')

    # Initialize the app with config settings
    Config.init_app(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app