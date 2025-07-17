import os
import subprocess
import shutil
import librosa
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# Print header using figlet if available, fallback to plain text
if shutil.which("figlet"):
    os.system("figlet -f slant 'm4a -> wav'")
else:
    print("=== m4a -> wav ===")

# Set up paths
DOWNLOADS_DIR = 'downloads'
OUTPUT_DIR = 'output'
SUPPORTED_INPUT_FORMATS = ['.m4a', '.opus', '.wav']

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

def convert_file(input_path: str, output_path: str):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"[+] Converting: {input_path}")
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            output_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[\u2713] Saved to: {output_path}")

        # Analyze key
        key = estimate_key(output_path)
        if key:
            new_path = os.path.splitext(output_path)[0] + f"_({key}).wav"
            os.rename(output_path, new_path)
            print(f"[♪] Renamed with key: {new_path}")

    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to convert {input_path}: {e}")

def get_all_audio_files(base_dir: str):
    files = []
    for root, _, filenames in os.walk(base_dir):
        for f in filenames:
            if any(f.lower().endswith(ext) for ext in SUPPORTED_INPUT_FORMATS):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base_dir)
                out_path = os.path.join(OUTPUT_DIR, os.path.splitext(rel_path)[0] + '.wav')
                files.append((full_path, out_path))
    return files

def clear_downloads_folder():
    print("\n[*] Clearing downloads directory...")
    for root, dirs, files in os.walk(DOWNLOADS_DIR, topdown=False):
        for name in files:
            if name != '.gitkeep':
                os.remove(os.path.join(root, name))
        for name in dirs:
            dir_path = os.path.join(root, name)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
    print("[\u2713] Downloads directory cleared.")

def main():
    print("[*] Scanning for audio files (.m4a, .opus, .wav)...")
    file_pairs = get_all_audio_files(DOWNLOADS_DIR)
    if not file_pairs:
        print("[!] No supported audio files found in downloads/. Exiting.")
        return

    print(f"[*] Found {len(file_pairs)} file(s) to convert.\n")

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(convert_file, src, dst) for src, dst in file_pairs]
        for future in as_completed(futures):
            future.result()

    print("\n[\u2713] All conversions completed.")
    clear_downloads_folder()

if __name__ == "__main__":
    main()
