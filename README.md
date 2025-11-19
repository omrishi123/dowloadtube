# Youtube-Video-Downloader

<p align="center">
<img height="350px" width="250px" src="https://github.com/VittalAB/Youtube-Video-Downloader/assets/59869004/4e20812b-1182-4069-9e49-7f071fb6e64c" />
</p>

### 📢 Exciting News! Introducing a Powerful YouTube Video Downloader! 🎥🎉

## 🔗 Link: [Project Link](https://github.com/VittalAB/Youtube-Video-Downloader)

## 🚀 Are you tired of relying on external software or plugins to download your favorite YouTube videos? Say goodbye to the hassle because our new YouTube Video Downloader is here to simplify the process! With just a single click, you can now download videos in MP4 and MP3 formats effortlessly.



## ✨ Features of Our YouTube Video Downloader:

 1️⃣ Real-time downloading: No more waiting! Experience lightning-fast video downloads in real time. <br>
 2️⃣ MP4 and MP3 formats: Choose your preferred format and get your videos downloaded hassle-free. <br>
 3️⃣ User-friendly interface: Our web application is designed to be intuitive and user-friendly, ensuring a seamless experience for all users. <br>
 4️⃣ Built with Flask and Tailwind CSS: Leveraging the power of Flask, a Python web framework, and styled with Tailwind CSS, our application offers a visually appealing and responsive interface.


### Youtube Video Downloader is Web Application built using Flask and Tailwind CSS which offers real time downloading of youtube videos with just a single click you can download videos in mp4 and mp3 format.

## Screenshots of Web application
<p align="center">
<img src="https://github.com/VittalAB/Youtube-Video-Downloader/assets/59869004/a12a8bbf-c400-41ac-a87d-74c08664f187"/>
</p>




# Requirements

### -> Flask
### -> Python 3.8+
### -> yt-dlp (upgraded from pytube for better YouTube API compatibility)
### -> ffmpeg

---

# Quick Setup & Run

## For Windows Users

### Option 1: Automated Setup (Easiest)
1. Run the setup script: `setup.bat`
2. Follow the prompts
3. After setup completes, run: `python app.py`
4. Open http://127.0.0.1:5000 in your browser

### Option 2: Manual Setup
1. Create and activate a Python virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate.ps1
# If script execution is blocked, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install ffmpeg:
   - Download from: [FFMPEg Download](https://ffmpeg.org/download.html)
   - Extract and add the `bin` folder to your System PATH environment variable
   - Verify installation:
```bash
ffmpeg -version
```

4. Run the application:
```bash
python app.py
```

5. Open http://127.0.0.1:5000 in your browser

## For Linux/macOS Users

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install ffmpeg:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Verify
ffmpeg -version
```

4. Run the application:
```bash
python app.py
```

5. Open http://127.0.0.1:5000 in your browser

---

## Troubleshooting

**Problem**: `HTTP Error 400: Bad Request` when downloading
- **Solution**: Ensure yt-dlp is up to date:
```bash
pip install --upgrade yt-dlp
```

**Problem**: `ffmpeg: command not found`
- **Solution**: Ensure ffmpeg is installed and on your PATH. Restart your terminal after installation.

**Problem**: Port 5000 already in use
- **Solution**: Modify `app.py` line 148 to use a different port:
```python
app.run(debug=False, port=5001, host="0.0.0.0")  # Change 5001 to any available port
```

---

## Download Link for FFMPEG

[FFMPEg Download](https://ffmpeg.org/download.html)

<p align="center">
<img height="500px" width="500px" src="https://github.com/VittalAB/Youtube-Video-Downloader/assets/59869004/54cb8a66-ea15-4a70-a152-cf7771e01642"/>
</p>



🌐 Don't miss out on this amazing opportunity to try out our YouTube Video Downloader. Visit the provided link and start downloading your favorite videos with ease. Feel free to share this post with your friends and let them experience the convenience too!

💡 Stay tuned for more exciting updates and features. We are committed to enhancing your video downloading experience and making it more enjoyable than ever before. Thank you for your support!

## #YouTubeVideoDownloader #VideoDownload #MP4 #MP3 #Flask #TailwindCSS #OnlineTools #DownloadVideos
