import os
import subprocess
import shutil
import uuid
import random
from datetime import datetime
import argparse

from highlight import find_highlight_segment
from subtitles import generate_subtitles_for_segment
from formatter import create_short, create_short_no_subtitles
from uploader import upload_video, setup_credentials, check_credentials_status
from downloader import get_cookie_options
from downloader import download_popular_videos, download_trending_videos, download_video_from_url

INPUT_DIR = "input_videos"
OUTPUT_DIR = "output_shorts"
PROCESSED_DIR = "processed"
TEMP_DIR = "temp"

CLIP_DURATION = 45  # seconds
SCHEDULE_HOURS_AHEAD = None  # Set to e.g. 6 if you want scheduling


def ensure_directories():
    for directory in [OUTPUT_DIR, PROCESSED_DIR, TEMP_DIR]:
        os.makedirs(directory, exist_ok=True)


def extract_audio(video_path, audio_path):
    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "2",
        audio_path
    ], check=True)


def generate_title(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    variants = [
        f"{base} 🤯",
        f"You Won’t Believe This...",
        f"This Changed Everything",
        f"Wait For It...",
        f"{base} (Insane Moment)"
    ]
    return random.choice(variants)


def process_video(video_path):
    try:
        print(f"\nProcessing: {video_path}")

        video_id = str(uuid.uuid4())
        audio_path = os.path.join(TEMP_DIR, f"{video_id}.wav")
        srt_path = os.path.join(TEMP_DIR, f"{video_id}.srt")
        output_path = os.path.join(OUTPUT_DIR, f"{video_id}.mp4")

        # 1️⃣ Extract audio
        extract_audio(video_path, audio_path)

        # 2️⃣ Detect highlight segment
        start, end = find_highlight_segment(audio_path, CLIP_DURATION)
        duration = end - start

        # 3️⃣ Generate subtitles (optional - skip if it fails)
        try:
            generate_subtitles_for_segment(video_path, srt_path, start, duration)
            subtitles_available = True
        except Exception as subtitle_error:
            print(f"Subtitle generation failed, creating video without subtitles: {subtitle_error}")
            subtitles_available = False

        # 4️⃣ Create vertical short
        if subtitles_available:
            create_short(
                input_video=video_path,
                start=start,
                duration=duration,
                subtitles=srt_path,
                output=output_path
            )
        else:
            # Create short without subtitles
            create_short_no_subtitles(
                input_video=video_path,
                start=start,
                duration=duration,
                output=output_path
            )

        # Clean up temp files immediately after video creation
        cleanup_temp_files(audio_path, srt_path)  # srt_path may not exist, but cleanup handles that

        # 5️⃣ Upload (optional - continue even if upload fails)
        title = generate_title(video_path)
        try:
            # Check credentials status
            cred_status = check_credentials_status()
            if not cred_status['valid']:
                print(f"YouTube Upload: {cred_status['message']}")
                print("Video processing complete but not uploaded.")
            else:
                upload_video(
                    file_path=output_path,
                    title=title,
                    description="Automated highlight clip",
                    tags=["shorts", "highlight"],
                    privacy_status="public",
                    publish_in_hours=SCHEDULE_HOURS_AHEAD
                )
                print("Video uploaded successfully.")
        except Exception as upload_error:
            print(f"Upload failed (video still saved): {upload_error}")
            if "credentials" in str(upload_error).lower() or "auth" in str(upload_error).lower():
                print("Tip: Run 'python app/main.py --setup-credentials' to set up YouTube API access")

        # 6️⃣ Move original to processed (always happens, even if upload fails)
        shutil.move(
            video_path,
            os.path.join(PROCESSED_DIR, os.path.basename(video_path))
        )

        print("Processing complete.")

    except Exception as e:
        print(f"Error processing {video_path}: {e}")
        # Clean up temp files even on error
        cleanup_temp_files(audio_path, srt_path)


def cleanup_temp_files(*files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)


def main():
    parser = argparse.ArgumentParser(description='Shorts AI - Automated YouTube Shorts Creator')
    parser.add_argument('--download-topic', type=str, help='Download popular videos from a specific topic')
    parser.add_argument('--download-trending', action='store_true', help='Download trending videos')
    parser.add_argument('--download-url', type=str, help='Download a video from a specific YouTube URL')
    parser.add_argument('--max-videos', type=int, default=5, help='Maximum number of videos to download (default: 5)')
    parser.add_argument('--process', action='store_true', help='Process existing videos in input_videos folder')
    parser.add_argument('--setup-credentials', action='store_true', help='Set up YouTube API credentials for automated uploads')
    parser.add_argument('--check-credentials', action='store_true', help='Check YouTube API credentials status')
    parser.add_argument('--check-cookies', action='store_true', help='Check YouTube cookie setup for age-restricted videos')

    args = parser.parse_args()

    print(f"\n===== Shorts Bot Run: {datetime.now()} =====")

    ensure_directories()

    # Handle setup
    if args.setup_credentials:
        setup_credentials()
        return

    if args.check_credentials:
        status = check_credentials_status()
        print(f"YouTube Credentials Status: {'✅ Valid' if status['valid'] else '❌ Invalid'}")
        print(f"Message: {status['message']}")
        return

    if args.check_cookies:
        print("Checking YouTube cookie setup...")
        cookie_opts = get_cookie_options()
        if 'cookiefile' in cookie_opts:
            print("✅ Cookies configured: Using cookies.txt file")
            print(f"   File: cookies/cookies.txt")
        elif 'cookiesfrombrowser' in cookie_opts:
            browser = cookie_opts['cookiesfrombrowser'][0]
            print(f"✅ Cookies configured: Using {browser} browser cookies")
        else:
            print("❌ No cookies configured")
            print("   Age-restricted videos may fail to download")
            print("   See COOKIES_SETUP.md for setup instructions")
        return

    # Handle downloading
    if args.download_topic:
        print(f"Downloading popular videos for topic: {args.download_topic}")
        download_popular_videos(args.download_topic, max_videos=args.max_videos)
        print("Download complete. Use --process to process the downloaded videos.")

    elif args.download_trending:
        print("Downloading trending videos")
        download_trending_videos(max_videos=args.max_videos)
        print("Download complete. Use --process to process the downloaded videos.")

    elif args.download_url:
        print(f"Downloading video from URL: {args.download_url}")
        download_video_from_url(args.download_url)
        print("Download complete. Use --process to process the downloaded videos.")

    # Handle processing
    if args.process or (not args.download_topic and not args.download_trending):
        videos = [
            f for f in os.listdir(INPUT_DIR)
            if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
        ]

        if not videos:
            print("No videos found in input_videos folder.")
            print("Use --download-topic 'your topic' or --download-trending to download videos first.")
            return

        print(f"Found {len(videos)} videos to process")
        for video in videos:
            full_path = os.path.join(INPUT_DIR, video)
            process_video(full_path)


if __name__ == "__main__":
    main()
