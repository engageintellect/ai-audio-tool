import os
import re
import openai
import json
from dotenv import load_dotenv
from tqdm import tqdm
from difflib import get_close_matches
from openai import OpenAI

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Directory to scan
TRACK_DIR = "output"

def collect_tracks():
    print("[*] Scanning output/ for .wav files...")
    tracks = []
    for root, _, files in os.walk(TRACK_DIR):
        for file in files:
            if file.endswith(".wav"):
                full_path = os.path.join(root, file)
                tracks.append(full_path)
    print(f"[*] Collected {len(tracks)} track(s) to analyze.\n")
    return tracks

def clean_filename(filepath):
    name = os.path.splitext(os.path.basename(filepath))[0]
    name = re.sub(r"\s*\([^)]*\)", "", name)
    name = re.sub(r"_+", " ", name)
    return name.strip()

def build_prompt(filenames):
    prompt = """You are a music expert with internet access and knowledge of modern music. For each track name listed below, return the accurate musical **key** and **tempo (BPM)** based on real metadata — do not guess or invent.

Many filenames include the artist and track name, sometimes in folder names or in parentheses. Clean up the names, infer the correct title and artist, and return:

Track Name: <clean artist + title>  
Key: <key>  
BPM: <bpm>  

Only include tracks you were able to identify confidently.

Here is the list:\n"""
    for f in filenames:
        prompt += f"{f}\n"
    return prompt.strip()

def get_metadata_responses(filenames):
    prompt = build_prompt(filenames)
    print("[🧠] Sending prompt to GPT-4o...\n" + "-"*60 + "\n")
    print(prompt + "\n" + "-"*60 + "\n")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful music metadata expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    reply = response.choices[0].message.content
    print("[🧠] GPT-4o Response:\n" + "-"*60)
    print(reply + "\n" + "-"*60 + "\n")
    return reply

def parse_response(response):
    results = []
    current = {}
    for line in response.splitlines():
        if line.startswith("Track Name:"):
            current = {}
            current["name"] = line.split("Track Name:")[1].strip()
        elif line.startswith("Key:"):
            current["key"] = line.split("Key:")[1].strip()
        elif line.startswith("BPM:"):
            current["bpm"] = line.split("BPM:")[1].strip()
            results.append(current)
    return results

def rename_files(filepaths, metadata_list):
    renamed = 0
    for meta in tqdm(metadata_list, desc="[🎵] Renaming"):
        match = None
        for f in filepaths:
            cleaned = clean_filename(f).lower()
            if all(part.lower() in cleaned for part in meta["name"].split(" - ")):
                match = f
                break
            else:
                close = get_close_matches(meta["name"].lower(), [cleaned], n=1, cutoff=0.8)
                if close:
                    match = f
                    break
        if match:
            dir_path = os.path.dirname(match)
            new_name = f"{meta['name']} ({meta['key']} - {meta['bpm']} BPM).wav"
            new_path = os.path.join(dir_path, new_name)
            os.rename(match, new_path)
            renamed += 1
        else:
            print(f"[!] Skipped: No match found for '{meta['name']}'")
    return renamed

if __name__ == "__main__":
    files = collect_tracks()
    clean_names = [clean_filename(f) for f in files]

    response = get_metadata_responses(clean_names)
    metadata = parse_response(response)

    count = rename_files(files, metadata)
    print(f"\n[✓] Metadata-based renaming complete. Renamed {count} file(s).")

