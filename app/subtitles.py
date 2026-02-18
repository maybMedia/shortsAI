import whisper

def generate_subtitles(video_path, output_srt):
    model = whisper.load_model("base")
    result = model.transcribe(video_path)

    with open(output_srt, "w") as f:
        for i, seg in enumerate(result["segments"]):
            f.write(f"{i+1}\n")
            f.write(f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")

def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"
