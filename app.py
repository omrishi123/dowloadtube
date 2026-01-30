''''
Created by Vittal Badami
Desc : - This is free youtube video downloader using pytube library.

'''

from flask import *
from yt_dlp import YoutubeDL
import os
from datetime import datetime
from flask import current_app
import shutil
import subprocess
import mimetypes
import urllib.parse

app = Flask(__name__)

audio_no = 0
video_no = 0

# shared counter was causing collisions between audio and video.
# use separate counters for audio and video
audio_i = 0
video_i = 0

if not os.path.exists('audios'):
    os.mkdir('audios')
if not os.path.exists('videos'):
    os.mkdir('videos')


def download_audio(link):
    global audio_i
    # simple cleanup: if too many files, reset the folder
    if len(os.listdir('audios')) > 50:
        shutil.rmtree('audios')
        os.mkdir('audios')
    
    try:
        # Download audio using yt-dlp and save using the video's title
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': './audios/%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': False,
            # Use TV client for best compatibility on Render (must be a list, not string)
            'extractor_args': {
                'youtube': {
                    'player_client': ['tv', 'android', 'web'],
                    'po_token': ['web']
                }
            },
        }
        # If a cookie file path is provided via env var, pass it to yt-dlp (or accept raw cookie content)
        cookie_env = os.environ.get('YTDLP_COOKIES_PATH') or os.environ.get('YTDLP_COOKIES')
        if cookie_env:
            # If the environment variable is a path to a file, use it directly.
            if os.path.exists(cookie_env):
                ydl_opts['cookiefile'] = cookie_env
            else:
                # Otherwise treat the env var as raw cookies content and write to a temp file.
                try:
                    import tempfile
                    tf = tempfile.NamedTemporaryFile(delete=False, prefix='ytdlp_cookies_', suffix='.txt', mode='w', encoding='utf-8')
                    tf.write(cookie_env)
                    tf.flush()
                    tf.close()
                    ydl_opts['cookiefile'] = tf.name
                except Exception as ee:
                    print(f"Could not write cookies content to temp file: {ee}")

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            # Use prepare_filename to compute the filename yt-dlp used for the downloaded file
            try:
                base_filename = ydl.prepare_filename(info)
            except Exception:
                base_filename = None

        audio_file = None
        if base_filename:
            # replace original extension with .mp3 (postprocessor output)
            mp3_candidate = os.path.splitext(base_filename)[0] + '.mp3'
            if os.path.exists(mp3_candidate):
                audio_file = mp3_candidate

        # If that didn't work, fallback to title-based search
        if audio_file is None and info:
            title = info.get('title')
            if title:
                def sanitize(name: str) -> str:
                    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
                sanitized = sanitize(title)
                candidate = os.path.join('audios', f"{sanitized}.mp3")
                if os.path.exists(candidate):
                    audio_file = candidate
                else:
                    candidate2 = os.path.join('audios', f"{title}.mp3")
                    if os.path.exists(candidate2):
                        audio_file = candidate2

        # Final fallback: pick most recent mp3
        if audio_file is None:
            mp3s = [f for f in os.listdir('audios') if f.lower().endswith('.mp3')]
            if mp3s:
                mp3s.sort(key=lambda x: os.path.getmtime(os.path.join('audios', x)), reverse=True)
                audio_file = os.path.join('audios', mp3s[0])

        if audio_file is None:
            raise FileNotFoundError('MP3 file not found after download')

        ret_file = audio_file
        with open("history.txt", "a") as myfile:
            myfile.write("\n" + f"{datetime.now().strftime('%d/%m/%y__%H:%M:%S')} --> {link}" + "\n")
        return ret_file
    
    except Exception as e:
        print(f"Error downloading audio: {e}")
        raise


def download_video(link, quality='best'):
    global video_i
    
    # simple cleanup: if too many files, reset the folder
    if len(os.listdir('videos')) > 200:
        shutil.rmtree('videos')
        os.mkdir('videos')
    
    try:
        # Map user-friendly quality choice to yt-dlp format string
        # Prefer mp4 container with both video and audio; fallback to webm+audio then convert
        quality_map = {
            'best': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/bestvideo+bestaudio[ext=webm]/bestvideo+bestaudio/best',
            '1080': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080][ext=mp4]+bestaudio/bestvideo[height<=1080]+bestaudio/best',
            '720': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720][ext=mp4]+bestaudio/bestvideo[height<=720]+bestaudio/best',
            '480': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480][ext=mp4]+bestaudio/bestvideo[height<=480]+bestaudio/best',
            '360': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360][ext=mp4]+bestaudio/bestvideo[height<=360]+bestaudio/best',
            'lowest': 'worst[ext=mp4]/worst',
        }

        fmt = quality_map.get(str(quality), 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/bestvideo+bestaudio[ext=webm]/bestvideo+bestaudio/best')

        # Use title-based filenames so downloaded files are saved with the video's title
        ydl_opts = {
            'format': fmt,
            'outtmpl': './videos/%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': False,
            'retries': 3,
            'fragment_retries': 3,
            'continuedl': True,
            'noplaylist': True,
            # FFmpegVideoConvertor will handle any format conversion to mp4
            'postprocessors': [
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }
            ],
            # Use TV client for best compatibility on Render (must be a list, not string)
            'extractor_args': {
                'youtube': {
                    'player_client': ['tv', 'android', 'web'],
                    'po_token': ['web']
                }
            },
        }
        # If a cookie file path is provided via env var, pass it to yt-dlp (or accept raw cookie content)
        cookie_env = os.environ.get('YTDLP_COOKIES_PATH') or os.environ.get('YTDLP_COOKIES')
        if cookie_env:
            # If the environment variable is a path to a file, use it directly.
            if os.path.exists(cookie_env):
                ydl_opts['cookiefile'] = cookie_env
            else:
                # Otherwise treat the env var as raw cookies content and write to a temp file.
                try:
                    import tempfile
                    tf = tempfile.NamedTemporaryFile(delete=False, prefix='ytdlp_cookies_', suffix='.txt', mode='w', encoding='utf-8')
                    tf.write(cookie_env)
                    tf.flush()
                    tf.close()
                    ydl_opts['cookiefile'] = tf.name
                except Exception as ee:
                    print(f"Could not write cookies content to temp file: {ee}")

        # Try download twice on failures that might be caused by transient fragment issues
        max_attempts = 2
        attempt = 0
        info = None
        while attempt < max_attempts:
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(link, download=True)
                break
            except Exception as de:
                # Clean up possible partial/fragment files that yt-dlp may have left behind
                import glob
                patterns = [os.path.join('videos', '*.part*'), os.path.join('videos', '*.part'), os.path.join('videos', '*.f*')]
                for pat in patterns:
                    for p in glob.glob(pat):
                        try:
                            os.remove(p)
                        except FileNotFoundError:
                            pass
                        except PermissionError:
                            pass
                        except Exception:
                            pass

                attempt += 1
                if attempt >= max_attempts:
                    # re-raise the original exception after attempted cleanup
                    raise
        
        # Determine the filename from the extracted info
        title = info.get('title') if 'info' in locals() and info else None
        def sanitize(name: str) -> str:
            return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()

        video_file = None
        if title:
            sanitized = sanitize(title)
            candidate = os.path.join('videos', f"{sanitized}.mp4")
            if os.path.exists(candidate):
                video_file = candidate
            else:
                candidate2 = os.path.join('videos', f"{title}.mp4")
                if os.path.exists(candidate2):
                    video_file = candidate2

        # Fallback: newest mp4 or any file
        if video_file is None:
            mp4s = [f for f in os.listdir('videos') if f.lower().endswith('.mp4')]
            if mp4s:
                mp4s.sort(key=lambda x: os.path.getmtime(os.path.join('videos', x)), reverse=True)
                video_file = os.path.join('videos', mp4s[0])
            else:
                files = os.listdir('videos')
                if files:
                    files.sort(key=lambda x: os.path.getmtime(os.path.join('videos', x)), reverse=True)
                    video_file = os.path.join('videos', files[0])

        if video_file is None:
            raise FileNotFoundError("Downloaded video file not found")

        ret_file = video_file
        with open("history.txt", "a") as myfile:
            myfile.write("\n" + f"{datetime.now().strftime('%d/%m/%y__%H:%M:%S')} --> {link}" + "\n")
        return ret_file
    
    except Exception as e:
        print(f"Error downloading video: {e}")
        raise

# home page


@app.route('/')
def hello_world():
    return render_template('index.html')

# for audio downloading


@app.route('/submit_audio', methods=['POST'])
def submit_audio():
    data = request.form.get('link')
    print(data)
    try:
        write_path = download_audio(data)
    except Exception as e:
        # Provide a helpful message for common yt-dlp errors (cookies / sign-in)
        print(f"download_audio error: {e}")
        msg = ("Error: yt-dlp failed to extract the audio. This often happens when YouTube asks to "
               "sign in or confirm you're not a bot. You can try supplying a cookies file via the "
               "environment variable `YTDLP_COOKIES_PATH`, or test with a different video. See: "
               "https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp")
        return Response(msg, status=502, mimetype='text/plain')
    print(write_path)
    abs_path = os.path.abspath(write_path)

    # Stream the MP3 to the client and delete the file after streaming completes
    def stream_and_delete(path, download_name=None, chunk_size=8192):
        if download_name is None:
            download_name = os.path.basename(path)
        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        def generator():
            try:
                with open(path, 'rb') as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
            finally:
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Could not delete audio file {path}: {e}")

        # Build Content-Disposition with ASCII fallback and RFC5987 encoded filename
        try:
            download_name.encode('latin-1')
            fallback = download_name
        except Exception:
            fallback = ''.join(c if ord(c) < 128 else '_' for c in download_name)

        encoded = urllib.parse.quote(download_name)
        content_disp = f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{encoded}"

        headers = {'Content-Disposition': content_disp}
        return Response(stream_with_context(generator()), mimetype=mime_type, headers=headers)

    return stream_and_delete(abs_path, os.path.basename(abs_path))


# for video downloading
@app.route('/submit', methods=['POST', 'GET'])
def submit():
    data = request.form.get('link')
    quality = request.form.get('quality', 'best')
    print(data, quality)
    try:
        write_path = download_video(data, quality)
    except Exception as e:
        print(f"download_video error: {e}")
        msg = ("Error: yt-dlp failed to extract the video. This often happens when YouTube asks to "
               "sign in or confirm you're not a bot. You can try supplying a cookies file via the "
               "environment variable `YTDLP_COOKIES_PATH`, or test with a different video. See: "
               "https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp")
        return Response(msg, status=502, mimetype='text/plain')
    print(write_path)
    abs_path = os.path.abspath(write_path)

    # Stream the file to the client and delete it from server after finished
    def stream_and_delete(path, download_name=None, chunk_size=8192):
        if download_name is None:
            download_name = os.path.basename(path)
        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        def generator():
            try:
                with open(path, 'rb') as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
            finally:
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Could not delete file {path}: {e}")

        # Build Content-Disposition with ASCII fallback and RFC5987 UTF-8 filename* to avoid
        # UnicodeEncodeError when the server sends headers containing non-Latin-1 chars.
        # Fallback filename: replace non-ascii chars with underscore
        try:
            download_name.encode('latin-1')
            fallback = download_name
        except Exception:
            fallback = ''.join(c if ord(c) < 128 else '_' for c in download_name)

        encoded = urllib.parse.quote(download_name)
        content_disp = f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{encoded}"

        headers = {
            'Content-Disposition': content_disp
        }

        return Response(stream_with_context(generator()), mimetype=mime_type, headers=headers)

    return stream_and_delete(abs_path, os.path.basename(abs_path))


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")
