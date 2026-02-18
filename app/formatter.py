import subprocess
import os

def create_short(input_video, start, duration, subtitles, output):
    # Escape the subtitles path for FFmpeg (replace backslashes with forward slashes)
    subtitles_path = subtitles.replace('\\', '/')

    # Subtitle styling: white text, black outline, larger font, centered
    subtitle_style = "force_style='FontName=Arial,FontSize=16,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=1,Outline=1,Alignment=2,MarginV=50'"

    cmd = [
        "ffmpeg",
        "-ss", str(start),
        "-i", input_video,
        "-t", str(duration),
        "-vf", f"crop=ih*(9/16):ih,scale=1080:1920:flags=lanczos,subtitles='{subtitles_path}':{subtitle_style}",
        "-c:a", "aac",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        output
    ]

    subprocess.run(cmd)

def create_short_no_subtitles(input_video, start, duration, output):
    cmd = [
        "ffmpeg",
        "-ss", str(start),
        "-i", input_video,
        "-t", str(duration),
        "-vf", "crop=ih*(9/16):ih,scale=1080:1920:flags=lanczos",
        "-c:a", "aac",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        output
    ]

    subprocess.run(cmd)
