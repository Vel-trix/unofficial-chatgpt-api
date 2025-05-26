from flask import Flask, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/aud/<video_id>')
def get_stream_urls(video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': False,
        'forcejson': True,
        'cookiefile': cookies_path  # Load cookies.txt from root
    }

    all_formats = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])

            for fmt in formats:
                if not fmt.get('url'):
                    continue
                all_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'resolution': fmt.get('resolution') or f"{fmt.get('width')}x{fmt.get('height')}",
                    'fps': fmt.get('fps'),
                    'vcodec': fmt.get('vcodec'),
                    'acodec': fmt.get('acodec'),
                    'filesize': fmt.get('filesize'),
                    'type': 'audio' if fmt.get('vcodec') == 'none' else ('video' if fmt.get('acodec') == 'none' else 'audio+video'),
                    'url': fmt.get('url'),
                })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'video_id': video_id, 'formats': all_formats})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
