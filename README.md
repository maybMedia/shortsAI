# Shorts AI - Automated YouTube Shorts Creator

This application automatically creates and uploads YouTube Shorts from videos by finding highlights, generating subtitles, and formatting them for vertical viewing.

## Features

- **YouTube Downloader**: Download popular videos from specific topics or trending videos
- **Highlight Detection**: Automatically find the most engaging segments in videos
- **Subtitle Generation**: Generate subtitles using OpenAI Whisper
- **Video Formatting**: Convert videos to vertical format suitable for YouTube Shorts
- **Automated Upload**: Upload processed shorts to YouTube with generated titles

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up YouTube API credentials (for uploading):
   - Create a project in Google Cloud Console
   - Enable YouTube Data API v3
   - Download client_secret.json to the `credentials/` folder

## Usage

### Download Videos

Download popular videos from a specific topic:
```bash
python app/main.py --download-topic "artificial intelligence" --max-videos 10
```

Download trending videos:
```bash
python app/main.py --download-trending --max-videos 5
```

### Process Videos

Process videos already in the `input_videos/` folder:
```bash
python app/main.py --process
```

### Combined Workflow

Download and process in one command:
```bash
python app/main.py --download-topic "machine learning" --max-videos 3 --process
```

### Examples

**Download trending videos and process them:**
```bash
python app/main.py --download-trending --max-videos 5 --process
```

**Download videos about gaming and process them:**
```bash
python app/main.py --download-topic "gaming tips" --max-videos 3 --process
```

**Download videos about cooking tutorials:**
```bash
python app/main.py --download-topic "easy recipes" --max-videos 10
```

## Directory Structure

- `input_videos/`: Source videos for processing
- `output_shorts/`: Generated YouTube Shorts
- `processed/`: Original videos after processing
- `temp/`: Temporary files (auto-cleaned)
- `credentials/`: YouTube API credentials

## Configuration

Edit the constants in `app/main.py`:
- `CLIP_DURATION`: Length of generated shorts (default: 45 seconds)
- `SCHEDULE_HOURS_AHEAD`: Schedule uploads for later (default: None)

## Requirements

- Python 3.8+
- FFmpeg
- YouTube API credentials (for uploading)

## Video Filtering

The downloader automatically filters videos to ensure they're suitable for shorts creation:

- **Duration**: 30 seconds to 20 minutes
- **Format**: MP4 videos at 1080p or lower for efficient processing

## Processing Features

- **Smart Subtitles**: Uses Whisper AI for transcription of highlight segments only (not entire video)
- **Highlight Detection**: Automatically finds engaging segments using audio analysis
- **Vertical Formatting**: Converts to 9:16 aspect ratio for YouTube Shorts
- **Error Recovery**: Continues processing even if upload or subtitle generation fails

## Performance Notes

- **Processing Time**: Video processing can take 5-15 minutes per video depending on length and hardware
- **Whisper Model**: Currently uses 'tiny' model for fast transcription. Change to 'base', 'small', 'medium', or 'large' in `app/subtitles.py` for better accuracy (but slower processing)
- **Disk Space**: Ensure adequate disk space (videos can generate large temporary WAV files)
- **CPU/GPU**: Whisper transcription runs on CPU by default. GPU acceleration can be enabled for faster processing
