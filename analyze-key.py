import os
import librosa
import numpy as np

OUTPUT_DIR = 'output'
SUPPORTED_FORMATS = ['.wav']

def estimate_key(filepath):
    try:
        y, sr = librosa.load(filepath)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_avg = np.mean(chroma, axis=1)
        pitch_classes = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                         'F#', 'G', 'G#', 'A', 'A#', 'B']
        estimated_key = pitch_classes[np.argmax(chroma_avg)]
        return estimated_key
    except Exception as e:
        print(f"[!] Failed to analyze key for {filepath}: {e}")
        return None

def rename_with_key(base_dir):
    print("[*] Analyzing .wav files in output/ and appending key to filenames...")
    for root, _, files in os.walk(base_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in SUPPORTED_FORMATS):
                if '_(' in file and file.endswith(').wav'):
                    continue  # Already renamed with key
                full_path = os.path.join(root, file)
                key = estimate_key(full_path)
                if key:
                    new_name = os.path.splitext(file)[0] + f"_({key}).wav"
                    new_path = os.path.join(root, new_name)
                    os.rename(full_path, new_path)
                    print(f"[♪] Renamed: {file} -> {new_name}")

if __name__ == "__main__":
    rename_with_key(OUTPUT_DIR)
    print("\n[\u2713] Key analysis and renaming complete.")

