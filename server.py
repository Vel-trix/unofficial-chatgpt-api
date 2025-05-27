from flask import Flask, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes and allows all origins

@app.route('/aud/<video_id>')
def get_stream_urls(video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': False,
        'forcejson': True,
        'cookiefile': "cookies.txt"
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', '')
            formats = info.get('formats', [])
            
            # Filter audio-only formats
            audio_formats = [
                fmt for fmt in formats 
                if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none' and fmt.get('url')
            ]
            
            if not audio_formats:
                return jsonify({'error': 'No audio formats found'}), 404
            
            # Find the best audio format (highest bitrate/quality)
            best_audio = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
            
            return jsonify({
                'url': best_audio.get('url'),
                'title': title
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
