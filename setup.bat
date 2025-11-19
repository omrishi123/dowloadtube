@echo off
REM Setup script for YouTube Video Downloader on Windows

echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo.
echo ========================================
echo Setup complete!
echo.
echo To run the application:
echo 1. Activate the venv: .\venv\Scripts\activate.bat
echo 2. Run: python app.py
echo 3. Open: http://127.0.0.1:5000
echo.
echo Make sure ffmpeg is installed and on PATH
echo Download: https://ffmpeg.org/download.html
echo ========================================
echo.
pause
