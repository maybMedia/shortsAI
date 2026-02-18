import subprocess
import os

def create_short(input_video, start, duration, subtitles, output):
    """
    Creates a vertical 9:16 short with subtitles and a blurred background.
    """
    # Escaping for Windows paths (converts C:\ to C\:\)
    subtitles_path = subtitles.replace('\\', '/').replace(':', '\\:')

    subtitle_style = (
        "force_style='FontName=Montserrat Bold,FontSize=16,"
        "PrimaryColour=&HFFFFFF,OutlineColour=&H000000,"
        "BorderStyle=1,Outline=1,Alignment=2,MarginV=60'"
        "Spacing=-1.0"
    )

    filter_complex = (
        # 1️⃣ Fill background: scale to COVER 1080x1920 then crop excess
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "boxblur=luma_radius=20:luma_power=1:chroma_radius=10:chroma_power=1,"
        "setsar=1[bg];"
        # 2️⃣ Foreground: scale to fit 1080 width (letterbox style)
        "[0:v]scale=1080:-2,setsar=1[fg];"
        # 3️⃣ Overlay and add subtitles
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,subtitles='{subtitles_path}':{subtitle_style}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-t", str(duration), # Fast seeking
        "-i", input_video,
        "-filter_complex", filter_complex,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac",
        output
    ]

    subprocess.run(cmd, check=True)


def create_short_no_subtitles(input_video, start, duration, output):
    """
    Creates a vertical 9:16 short with a blurred background (No Subtitles).
    """
    filter_complex = (
        # 1️⃣ Fill background: scale to COVER 1080x1920 then crop excess
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "boxblur=luma_radius=20:luma_power=1:chroma_radius=10:chroma_power=1,"
        "setsar=1[bg];"
        # 2️⃣ Foreground: scale to fit 1080 width
        "[0:v]scale=1080:-2,setsar=1[fg];"
        # 3️⃣ Overlay only
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-t", str(duration),
        "-i", input_video,
        "-filter_complex", filter_complex,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac",
        output
    ]

    subprocess.run(cmd, check=True)