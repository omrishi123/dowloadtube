FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install ffmpeg and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create directories for audio and video downloads
RUN mkdir -p audios videos

# Expose port (Render sets $PORT env variable)
EXPOSE 5000

# Use gunicorn to run Flask; bind to port Render provides
CMD gunicorn -b 0.0.0.0:$PORT app:app --workers 1 --threads 4 --timeout 120
