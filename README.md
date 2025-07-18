# 🎧 ai-audio-tool

Batch convert audio files to `.wav`, preserve folder structure, clean up after, and optionally analyze them using GPT-4o to auto-rename with **musical key** and **tempo**.

---

## 🔧 Features

- 🔍 Recursively scans `downloads/` for `.m4a`, `.opus`, and `.wav` files
- 🔄 Converts to `.wav` using `ffmpeg`, preserving folder structure
- 🚀 Parallel processing for speed
- 🧼 Automatically clears converted files from `downloads/` (except `.gitkeep`)
- 💬 Clean CLI with progress logging and friendly output
- 🧠 GPT-4o integration to rename tracks by key + BPM (uses `analyze-key-gpt4o.py`)
- 🧪 `--dry-run` mode to preview changes without touching files
- 🎨 Fancy ASCII banner with `figlet` (fallback included)

---

## 📁 Project Structure

```
ai-audio-tool/
├── downloads/               # Drop your audio files in here
│   └── .gitkeep             # Keeps directory in Git
├── output/                  # Converted files show up here
├── main.py                  # Main batch conversion + GPT automation
├── analyze-key-gpt4o.py     # GPT-based key/BPM analyzer and renamer
├── requirements.txt         # Python dependencies
├── .env                     # Stores your OpenAI API key
└── README.md                # You're reading this
```

---

## ⚙️ Setup

### 1. Install system dependencies

#### ffmpeg (required)

```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg
```

#### figlet (optional, for banner)

```bash
# macOS
brew install figlet

# Ubuntu
sudo apt install figlet
```

---

### 2. Install Python dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt`:

```txt
python-dotenv
openai
tqdm
```

---

### 3. Configure OpenAI

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your-api-key-here
```

You can get your key from: https://platform.openai.com/account/api-keys

---

## 🚀 Usage

### Basic usage

Drop `.m4a`, `.opus`, or `.wav` files into `downloads/` (folders are fine):

```bash
python main.py
```

This will:

1. Convert all supported files in `downloads/` to `.wav`
2. Save the converted files to `output/`, preserving subfolders
3. Clean up the `downloads/` directory (excluding `.gitkeep`)
4. Run `analyze-key-gpt4o.py` to:
   - Send filenames to GPT-4o
   - Get key + BPM metadata
   - Rename each `.wav` file to:  
     `Track Name (Key - BPM).wav`

---

### Dry-run mode

Preview all actions without converting or deleting anything:

```bash
python main.py --dry-run
```

This is useful for testing file paths and GPT output before running for real.

---

## 🧠 GPT Track Analysis

After conversion, `analyze-key-gpt4o.py`:

- Scans `output/` for `.wav` files
- Sends a cleaned list of filenames to GPT-4o
- Parses the response to extract musical metadata
- Renames matched files with their key + BPM

Example:

```bash
Track Name: The Weeknd - Blinding Lights  
Key: F# Minor  
BPM: 171

➡️  output/The Weeknd - Blinding Lights (F# Minor - 171 BPM).wav
```

If no confident match is found, it skips the file and logs it.

---

## 🧪 Notes

- Instrumentals and obscure tracks may not return metadata from GPT
- GPT relies on accurate filenames — try to include artist and title
- `.gitkeep` ensures empty `downloads/` and `output/` dirs are preserved in Git
- You can comment out GPT automation in `main.py` if not needed

---

## 🫶 Credits

Built with love and `ffmpeg`, OpenAI, tqdm, and way too many `.m4a` files.

```bash
figlet m4a-wav
```

--- 

MIT License.

