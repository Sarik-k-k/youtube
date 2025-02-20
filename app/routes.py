from flask import Blueprint, render_template, request, send_file, jsonify
from .utils.universal_downloader import download_youtube_content
from .utils.thumbnail_downloader import download_thumbnail
import os 
import io

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/download_video', methods=['GET', 'POST'])
def video_download():
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            file_path = download_youtube_content(url, 'video')
            if file_path:
                return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
            else:
                return jsonify({"error": "Download failed"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return render_template('video_download.html')

@main.route('/download_audio', methods=['GET', 'POST'])
def audio_download():
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            file_path = download_youtube_content(url, 'audio')
            if file_path:
                return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
            else:
                return jsonify({"error": "Download failed"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return render_template('audio_download.html')

@main.route('/download_thumbnail', methods=['GET', 'POST'])
def thumbnail_download():
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            result = download_thumbnail(url)
            if result:
                filename, thumbnail_bytes, content_type = result
                return send_file(
                    io.BytesIO(thumbnail_bytes),
                    as_attachment=True,
                    download_name=filename,
                    mimetype=content_type
                )
            else:
                return jsonify({"error": "Download failed"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template('thumbnail_download.html')

@main.route('/download_playlist', methods=['GET', 'POST'])
def playlist_download():
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            download_folder = download_youtube_content(url, 'playlist')
            if download_folder:
                return jsonify({
                    "message": "Playlist downloaded successfully",
                    "folder": download_folder
                })
            else:
                return jsonify({"error": "Download failed"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return render_template('playlist_download.html')