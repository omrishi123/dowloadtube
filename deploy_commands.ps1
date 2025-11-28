# deploy_commands.ps1
# PowerShell script with commands to prepare repo and test locally before deploying to Render.
# Copy and paste into PowerShell (run from project root: C:\Users\pcs6\Desktop\MY APPLICATION PROJECTS\Youtube-Video-Downloader)

$ErrorActionPreference = 'Stop'
Write-Host "Running deploy prep script in: $(Get-Location)" -ForegroundColor Cyan

# 1) Ensure we are in a git repo
if (-not (Test-Path .git)) {
  Write-Host "This directory is not a git repository. Initialize or cd into the repo." -ForegroundColor Red
  exit 1
}

# 2) Remove venv from git tracking (safe - does not delete local venv)
if (Test-Path venv) {
  Write-Host "Removing venv from git tracking..." -ForegroundColor Yellow
  try {
    & git rm -r --cached venv
  } catch {
    Write-Host "git rm returned non-zero (maybe already removed)" -ForegroundColor Yellow
  }
} else {
  Write-Host "No venv/ folder found locally; skipping git rm." -ForegroundColor Green
}

# 3) Ensure venv/ is in .gitignore
if (-not (Test-Path .gitignore)) { New-Item -Path .gitignore -ItemType File -Force | Out-Null }
$gitignoreText = Get-Content .gitignore -ErrorAction SilentlyContinue -Raw
if ($gitignoreText -notmatch "(?m)^venv/|(?m)^venv$") {
  Add-Content -Path .gitignore -Value "`n# Local Python virtualenv`nvenv/"
  Write-Host "Appended venv/ to .gitignore" -ForegroundColor Green
} else {
  Write-Host "venv/ already present in .gitignore" -ForegroundColor Green
}

# 4) Ensure required deployment files exist (create only if missing)
if (-not (Test-Path Dockerfile)) {
  Write-Host "Creating Dockerfile..." -ForegroundColor Yellow
  @"
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
"@ | Set-Content Dockerfile
} else { Write-Host "Dockerfile already exists; leaving it alone." -ForegroundColor Green }

if (-not (Test-Path .dockerignore)) {
  Write-Host "Creating .dockerignore..." -ForegroundColor Yellow
  @"
__pycache__
*.pyc
*.pyo
*.pyd
.env
venv
env
.git
.gitignore
node_modules
*.db
*.sqlite3
.DS_Store
*.log
*.txt
audios/
videos/
.vscode
.idea
"@ | Set-Content .dockerignore
} else { Write-Host ".dockerignore exists; leaving it alone." -ForegroundColor Green }

if (-not (Test-Path requirements.txt)) {
  Write-Host "Creating requirements.txt..." -ForegroundColor Yellow
  @"
Flask==3.0.0
yt-dlp>=2024.11.12
gunicorn>=20.1
"@ | Set-Content requirements.txt
} else { Write-Host "requirements.txt exists; leaving it alone." -ForegroundColor Green }

# 5) Stage and commit changes (if any)
Write-Host "Staging deployment-related files..." -ForegroundColor Cyan
try {
  & git add Dockerfile .dockerignore requirements.txt .gitignore
} catch {
  Write-Host "git add returned non-zero" -ForegroundColor Yellow
}

# Commit with safe message, but don't fail if nothing to commit
$commitMessage = 'chore: deployment prep - remove venv, add Dockerfile & requirements'
try {
  & git commit -m $commitMessage
} catch {
  Write-Host "Nothing to commit or commit failed." -ForegroundColor Yellow
}

# 6) Push to origin main
Write-Host "Pushing to origin main..." -ForegroundColor Cyan
try {
  & git push origin main
  Write-Host "Push succeeded." -ForegroundColor Green
} catch {
  Write-Host "Push failed: $_" -ForegroundColor Red
  exit 1
}

# 7) (Optional) Local Docker build + run for testing
if (Get-Command docker -ErrorAction SilentlyContinue) {
  Write-Host "Building Docker image locally (ytdl-app)..." -ForegroundColor Cyan
  docker build -t ytdl-app .
  Write-Host "To run locally: docker run -p 5000:5000 -e PORT=5000 ytdl-app" -ForegroundColor Green
} else {
  Write-Host "Docker not found on PATH. Install Docker Desktop to run locally (optional)." -ForegroundColor Yellow
}

Write-Host "" -ForegroundColor Cyan
Write-Host "Done. Next steps:" -ForegroundColor Cyan
Write-Host " - On Render: create a new Web Service, connect this GitHub repo; Render will detect the Dockerfile and build it." -ForegroundColor Cyan
Write-Host " - If Render fails with missing requirements, ensure requirements.txt is present in repo root." -ForegroundColor Cyan
Write-Host " - Test the public URL Render provides after deploy." -ForegroundColor Cyan

# End of script
