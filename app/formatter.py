import subprocess

def create_short(input_video, start, duration, subtitles, output):
    cmd = [
        "ffmpeg",
        "-ss", str(start),
        "-i", input_video,
        "-t", str(duration),
        "-vf", "crop=ih*(9/16):ih,scale=1080:1920,subtitles=" + subtitles,
        "-c:a", "aac",
        output
    ]

    subprocess.run(cmd)
