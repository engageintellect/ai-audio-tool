import argparse
import os
import subprocess
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# Paths
DOWNLOADS_DIR = 'downloads'
OUTPUT_DIR = 'output'
SUPPORTED_INPUT_FORMATS = ['.m4a', '.opus', '.wav']
GPT_SCRIPT = 'analyze-key-gpt4o.py'  # Make sure this file exists and is executable


def print_header():
    """Display fancy title if figlet is installed."""
    if shutil.which("figlet"):
        os.system("figlet -f slant 'm4a -> wav'")
    else:
        print("=== m4a -> wav ===")


def convert_file(input_path: str, output_path: str, dry_run: bool = False):
    """Convert a single file to WAV using ffmpeg."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"[+] Converting: {input_path}")
    if dry_run:
        print(f"    ↳ [dry-run] Would save to: {output_path}")
        return

    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-acodec', 'pcm_s16le', '-ar', '44100', output_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"    ↳ [✓] Saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"    ↳ [!] Failed to convert {input_path}: {e}")


def get_all_audio_files(base_dir: str):
    """Find all supported audio files and return (input, output) pairs."""
    files = []
    for root, _, filenames in os.walk(base_dir):
        for f in filenames:
            if any(f.lower().endswith(ext) for ext in SUPPORTED_INPUT_FORMATS):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base_dir)
                out_path = os.path.join(OUTPUT_DIR, os.path.splitext(rel_path)[0] + '.wav')
                files.append((full_path, out_path))
    return files


def clear_downloads_folder(dry_run: bool = False):
    """Delete all files in downloads/ except .gitkeep."""
    print("\n[*] Cleaning downloads folder...")
    for root, dirs, files in os.walk(DOWNLOADS_DIR, topdown=False):
        for name in files:
            if name != '.gitkeep':
                path = os.path.join(root, name)
                if dry_run:
                    print(f"    ↳ [dry-run] Would remove file: {path}")
                else:
                    os.remove(path)
        for name in dirs:
            dir_path = os.path.join(root, name)
            if not os.listdir(dir_path):
                if dry_run:
                    print(f"    ↳ [dry-run] Would remove empty dir: {dir_path}")
                else:
                    os.rmdir(dir_path)
    print("[✓] Downloads cleanup complete.")


def run_gpt_analysis_script(dry_run: bool = False):
    """Run analyze-key-gpt4o.py to rename tracks using GPT metadata."""
    if dry_run:
        print("\n[🧠] Skipping GPT analysis (dry-run mode).")
        return

    print("\n[🧠] Analyzing converted tracks using GPT-4o...\n")
    result = subprocess.run(['python3', GPT_SCRIPT])
    if result.returncode == 0:
        print("[✓] GPT-based renaming completed successfully.")
    else:
        print("[!] GPT-based renaming failed or exited with error.")


def main(dry_run: bool = False):
    print_header()
    print("[*] Scanning for .m4a, .opus, and .wav files in downloads/...\n")

    file_pairs = get_all_audio_files(DOWNLOADS_DIR)
    if not file_pairs:
        print("[!] No files found. Exiting.")
        return

    print(f"[*] Found {len(file_pairs)} file(s) to convert.\n")

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(convert_file, src, dst, dry_run) for src, dst in file_pairs]
        for future in as_completed(futures):
            future.result()

    print("\n[✓] All conversions completed.")
    clear_downloads_folder(dry_run)

    # Kick off GPT-4o analysis
    run_gpt_analysis_script(dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert audio files in 'downloads/' to WAV format in 'output/'.")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without making changes.")
    args = parser.parse_args()

    main(dry_run=args.dry_run)

