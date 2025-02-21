from dotenv import load_dotenv
import os

# Load environment variables before importing app
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment variable (Render.com uses PORT)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)