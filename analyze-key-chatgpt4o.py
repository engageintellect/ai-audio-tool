import os
import re
from pathlib import Path
from difflib import SequenceMatcher
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SETTINGS
OUTPUT_DIR = 'output'
SUPPORTED_FORMATS = ['.wav']
BATCH_SIZE = 20

PROMPT_TEMPLATE = """
You are a music expert with internet access and knowledge of modern music. For each track name listed below, return the accurate musical **key** and **tempo (BPM)** based on real metadata — do not guess or invent.

Many filenames include the artist and track name, sometimes in folder names or in parentheses. Clean up the names, infer the correct title and artist, and return:

Track Name: <clean artist + title>
Key: <key>
BPM: <bpm>

Only include tracks you were able to identify confidently.

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
    print(f"\n[🧠] Sending prompt to GPT-4o...\n{'-'*60}\n{prompt}\n{'-'*60}")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    text = response.choices[0].message.content
    print(f"\n[🧠] GPT-4o Response:\n{'-'*60}\n{text}\n{'-'*60}")
    return text

def parse_gpt_response(response):
    parsed = {}
    entries = re.split(r"(?=Track Name:)", response.strip())
    for entry in entries:
        title_match = re.search(r"Track Name:\s*(.+)", entry)
        key_match = re.search(r"Key:\s*(.+)", entry)
        bpm_match = re.search(r"BPM:\s*(.+)", entry)
        if title_match and key_match and bpm_match:
            title = title_match.group(1).strip()
            key = key_match.group(1).strip()
            bpm = bpm_match.group(1).strip()
            parsed[title] = f"_({key}_{bpm}bpm)"
    return parsed

def clean_title_for_match(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def fuzzy_match(gpt_title, filename_title, threshold=0.7):
    return SequenceMatcher(None, clean_title_for_match(gpt_title), clean_title_for_match(filename_title)).ratio() > threshold

def rename_files(title_map, metadata):
    renamed = 0
    for messy_title, path in title_map.items():
        match_key = None
        for gpt_title, suffix in metadata.items():
            if fuzzy_match(gpt_title, messy_title):
                match_key = suffix
                break
        if not match_key:
            print(f"[!] Skipped: No match found for '{messy_title}'")
            continue
        base, ext = os.path.splitext(path)
        if match_key in path:
            print(f"[~] Already renamed: {os.path.basename(path)}")
            continue
        new_path = base + match_key + ext
        os.rename(path, new_path)
        print(f"[♪] Renamed: {os.path.basename(path)} → {os.path.basename(new_path)}")
        renamed += 1
    return renamed

def main():
    print("[*] Scanning output/ for .wav files...")
    title_map = collect_track_titles(OUTPUT_DIR)
    if not title_map:
        print("[!] No .wav files found in output/. Exiting.")
        return

    print(f"[*] Collected {len(title_map)} track(s) to analyze.\n")
    all_metadata = {}

    for batch in batch_titles(title_map, BATCH_SIZE):
        gpt_response = ask_gpt_for_metadata(batch)
        batch_metadata = parse_gpt_response(gpt_response)
        all_metadata.update(batch_metadata)

    renamed = rename_files(title_map, all_metadata)
    print(f"\n[✓] Metadata-based renaming complete. Renamed {renamed} file(s).")

if __name__ == "__main__":
    main()

