import os
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()
client = OpenAI()  # API key loaded from OPENAI_API_KEY

# SETTINGS
OUTPUT_DIR = 'output'
SUPPORTED_FORMATS = ['.wav']
BATCH_SIZE = 20

PROMPT_TEMPLATE = """
You're a musicologist. Given a list of messy song titles and artist names, return the musical key and BPM (tempo) for each track. Only include entries you are confident about. Format the results like this:

Track Name: <original name>
Key: <key>
BPM: <tempo>

Here is the list:
{songs}
"""

def collect_track_titles(base_dir):
    title_map = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in SUPPORTED_FORMATS):
                base_name = os.path.splitext(file)[0]
                parent_name = Path(root).name
                messy_title = f"{parent_name} - {base_name}" if parent_name not in base_name else base_name
                title_map[messy_title] = os.path.join(root, file)
    return title_map

def batch_titles(titles, size):
    items = list(titles.keys())
    for i in range(0, len(items), size):
        yield items[i:i + size]

def ask_gpt_for_metadata(batch):
    prompt = PROMPT_TEMPLATE.format(songs="\n".join(batch))
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def parse_gpt_response(response):
    parsed = {}
    entries = response.strip().split("Track Name:")
    for entry in entries:
        if not entry.strip():
            continue
        lines = entry.strip().splitlines()
        title = lines[0].strip()
        key = None
        bpm = None
        for line in lines[1:]:
            if line.lower().startswith("key"):
                key = line.split(":")[-1].strip()
            if line.lower().startswith("bpm") or "tempo" in line.lower():
                bpm = line.split(":")[-1].strip()
        if key and bpm:
            parsed[title] = f"_({key}_{bpm}bpm)"
    return parsed

def rename_files(title_map, metadata):
    for messy_title, path in title_map.items():
        suffix = metadata.get(messy_title)
        if not suffix:
            continue
        base, ext = os.path.splitext(path)
        if suffix in path:
            continue  # already renamed
        new_path = base + suffix + ext
        os.rename(path, new_path)
        print(f"[♪] Renamed: {os.path.basename(path)} → {os.path.basename(new_path)}")

def main():
    print("[*] Scanning output/ for .wav files...")
    title_map = collect_track_titles(OUTPUT_DIR)
    if not title_map:
        print("[!] No .wav files found in output/. Exiting.")
        return

    print(f"[*] Collected {len(title_map)} track(s) to analyze.\n")
    all_metadata = {}
    for batch in batch_titles(title_map, BATCH_SIZE):
        print(f"[*] Sending batch of {len(batch)} tracks to GPT...")
        gpt_response = ask_gpt_for_metadata(batch)
        batch_metadata = parse_gpt_response(gpt_response)
        all_metadata.update(batch_metadata)

    rename_files(title_map, all_metadata)
    print("\n[✓] Metadata-based renaming complete.")

if __name__ == "__main__":
    main()
