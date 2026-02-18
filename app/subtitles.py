import whisper

def generate_subtitles(video_path, output_srt):
    # Use 'tiny' model for faster processing (can be changed to 'base', 'small', 'medium', 'large')
    model = whisper.load_model("tiny")
    result = model.transcribe(video_path)

    with open(output_srt, "w") as f:
        for i, seg in enumerate(result["segments"]):
            f.write(f"{i+1}\n")
            f.write(f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")

def generate_subtitles_for_segment(video_path, output_srt, start_time, duration):
    """
    Generate subtitles for a specific time segment of the video.
    Adjusts timing to start from 0 and makes text more concise with shorter segments.
    """
    # Use 'tiny' model for faster processing
    model = whisper.load_model("tiny")
    result = model.transcribe(video_path)

    end_time = start_time + duration

    # Filter segments that overlap with our highlight segment
    relevant_segments = []
    for seg in result["segments"]:
        # Include segments that overlap with our time range
        if seg['start'] < end_time and seg['end'] > start_time:
            relevant_segments.append(seg)

    if not relevant_segments:
        # If no segments found, create empty subtitle file
        with open(output_srt, "w") as f:
            f.write("")
        return

    with open(output_srt, "w") as f:
        subtitle_index = 1

        for seg in relevant_segments:
            # Adjust timing to be relative to the start of our segment
            adjusted_start = max(0, seg['start'] - start_time)
            adjusted_end = min(duration, seg['end'] - start_time)

            # Skip segments that are now outside our duration
            if adjusted_end <= 0:
                continue

            # Clean up the text - make it more concise
            text = seg['text'].strip()
            # Remove extra whitespace
            text = ' '.join(text.split())

            # Break long text into shorter chunks (aim for 3-5 words per subtitle)
            words = text.split()
            if len(words) > 5:
                # Create multiple subtitle entries for long text
                chunk_size = 4  # words per subtitle
                for i in range(0, len(words), chunk_size):
                    chunk_words = words[i:i + chunk_size]
                    chunk_text = ' '.join(chunk_words)

                    # Calculate timing for this chunk
                    chunk_duration = (adjusted_end - adjusted_start) / max(1, len(words) // chunk_size + 1)
                    chunk_start = adjusted_start + (i // chunk_size) * chunk_duration
                    chunk_end = min(adjusted_end, chunk_start + chunk_duration)

                    f.write(f"{subtitle_index}\n")
                    f.write(f"{format_time(chunk_start)} --> {format_time(chunk_end)}\n")
                    f.write(f"{chunk_text}\n\n")
                    subtitle_index += 1
            else:
                # Short text - use as is, but still limit length
                if len(text) > 50:
                    text = text[:47] + "..."

                f.write(f"{subtitle_index}\n")
                f.write(f"{format_time(adjusted_start)} --> {format_time(adjusted_end)}\n")
                f.write(f"{text}\n\n")
                subtitle_index += 1

def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"
