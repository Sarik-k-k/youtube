# YouTube Utility

Flask application for downloading YouTube content.

## Features
- Video downloads
- Audio extraction
- Playlist downloads
- Thumbnail downloads

## Local Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python run.py
```

## Environment Variables
- SECRET_KEY: Flask secret key
- FLASK_DEBUG: Set to False in production

## Deployment
Configured for Railway.app deployment