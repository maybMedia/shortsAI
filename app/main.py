import os
import subprocess
import shutil
import uuid
import random
from datetime import datetime

from highlight import find_highlight_segment
from subtitles import generate_subtitles
from formatter import create_short
from uploader import upload_video

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

        # 3️⃣ Generate subtitles
        generate_subtitles(video_path, srt_path)

        # 4️⃣ Create vertical short
        create_short(
            input_video=video_path,
            start=start,
            duration=duration,
            subtitles=srt_path,
            output=output_path
        )

        # 5️⃣ Upload
        title = generate_title(video_path)

        upload_video(
            file_path=output_path,
            title=title,
            description="Automated highlight clip",
            tags=["shorts", "highlight"],
            privacy_status="public",
            publish_in_hours=SCHEDULE_HOURS_AHEAD
        )

        # 6️⃣ Move original to processed
        shutil.move(
            video_path,
            os.path.join(PROCESSED_DIR, os.path.basename(video_path))
        )

        # 7️⃣ Cleanup temp files
        cleanup_temp_files(audio_path, srt_path)

        print("Processing complete.")

    except Exception as e:
        print(f"Error processing {video_path}: {e}")


def cleanup_temp_files(*files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)


def main():
    print(f"\n===== Shorts Bot Run: {datetime.now()} =====")

    ensure_directories()

    videos = [
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith(".mp4")
    ]

    if not videos:
        print("No new videos found.")
        return

    for video in videos:
        full_path = os.path.join(INPUT_DIR, video)
        process_video(full_path)


if __name__ == "__main__":
    main()
