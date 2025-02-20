import os
import yt_dlp
import unicodedata
import re

def sanitize_filename(filename):
    """
    Sanitize filename to remove invalid characters and limit length.
    """
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^\w\-_\. ]', '_', filename)
    max_length = 255
    return filename[:max_length]

def download_youtube_content(url, download_type='video'):
    """
    Universal downloader for YouTube videos and playlists.
    
    Args:
        url (str): YouTube video or playlist URL.
        download_type (str): 'video', 'audio', or 'playlist'.
    
    Returns:
        str: Path to downloaded content.
    """
    base_download_dir = 'D:/testing projects/youtube all features/app/downloads'
    video_dir = os.path.join(base_download_dir, 'videos')
    audio_dir = os.path.join(base_download_dir, 'audio')
    playlist_dir = os.path.join(base_download_dir, 'playlists')
    
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(playlist_dir, exist_ok=True)

    # Select appropriate options based on the requested download type.
    if download_type == 'video':
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(video_dir, '%(title)s.%(ext)s')
        }
    elif download_type == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
            'outtmpl': os.path.join(audio_dir, '%(title)s.%(ext)s')
        }
    elif download_type == 'playlist':
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(playlist_dir, '%(playlist_title)s', '%(title)s.%(ext)s')
        }
    else:
        raise ValueError("Invalid download type")

    ydl_opts.update({
        'restrictfilenames': True,
        'nooverwrites': True,
        'no_color': True,
        'progress_hooks': [print_progress]
    })

    try:
        # This single extract_info call performs extraction and downloads directly.
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # If it's a playlist, adjust the reported download_path accordingly.
            if 'entries' in info:
                download_path = os.path.join(playlist_dir, info.get('playlist_title', 'Unnamed Playlist'))
            else:
                download_path = ydl.prepare_filename(info)
                # For audio downloads, update the expected file extension to .mp3.
                if download_type == 'audio':
                    base, _ = os.path.splitext(download_path)
                    download_path = base + '.mp3'

            if not os.path.exists(download_path):
                raise FileNotFoundError(f"File not found: {download_path}")

        return download_path

    except Exception as e:
        print(f"Download error: {e}")
        return None

def print_progress(d):
    """Optional progress tracking hook"""
    if d.get('status') == 'finished':
        print('Download complete')
    elif d.get('status') == 'downloading':
        downloaded_bytes = d.get('downloaded_bytes', 0)
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        if total_bytes > 0:
            percent = downloaded_bytes * 100 / total_bytes
            print(f'Downloading: {percent:.1f}%')

if __name__ == '__main__':
    url = input("Enter YouTube URL (video/playlist): ")
    # Directly download content without first caching info in a separate extraction.
    result = download_youtube_content(url)
    if result:
        print(f"Successfully downloaded to: {result}")
    else:
        print("Download failed")