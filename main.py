import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up paths
DOWNLOADS_DIR = 'downloads'
OUTPUT_DIR = 'output'

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
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to convert {input_path}: {e}")

def get_all_m4a_files(base_dir: str):
    files = []
    for root, _, filenames in os.walk(base_dir):
        for f in filenames:
            if f.lower().endswith('.m4a'):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base_dir)
                out_path = os.path.join(OUTPUT_DIR, os.path.splitext(rel_path)[0] + '.wav')
                files.append((full_path, out_path))
    return files

def main():
    print("[*] Scanning for .m4a files...")
    file_pairs = get_all_m4a_files(DOWNLOADS_DIR)
    print(f"[*] Found {len(file_pairs)} file(s) to convert.\n")

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(convert_file, src, dst) for src, dst in file_pairs]
        for future in as_completed(futures):
            future.result()

    print("\n[\u2713] All conversions completed.")

if __name__ == "__main__":
    main()

