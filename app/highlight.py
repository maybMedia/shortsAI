import librosa
import numpy as np

def find_highlight_segment(audio_path, clip_length=45):
    y, sr = librosa.load(audio_path)

    energy = np.array([
        np.sum(np.abs(y[i:i+sr]))
        for i in range(0, len(y), sr)
    ])

    peak_second = np.argmax(energy)

    start = max(0, peak_second - clip_length // 2)
    end = start + clip_length

    return start, end
