from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        logger.error(f'Page not found: {error}')
        return jsonify({'error': 'Not Found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Server Error: {error}')
        return jsonify({'error': 'Internal Server Error'}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f'Unhandled Exception: {error}')
        return jsonify({'error': str(error)}), 500