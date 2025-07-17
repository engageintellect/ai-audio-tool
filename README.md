# m4a-wav-batch-transcoder

Batch convert all `.m4a` files to `.wav`, preserving folder structure, using `ffmpeg`.

## 🔧 Features
- Recursively traverse the `downloads/` directory
- Convert all `.m4a` files to `.wav`
- Preserve folder structure in the `output/` directory
- Parallel processing for faster conversion
- Clean CLI-style logging with success/failure feedback
- **Automatically clears converted files from `downloads/`, preserving `.gitkeep`**
- Prints a cool ASCII art header using `figlet`, with a fallback if not installed

## 📁 Project Structure
```
m4a-wav-batch-transcoder/
├── downloads/       # Place all your .m4a files and folders here
│   └── .gitkeep     # Ensures folder remains in Git
├── output/          # Converted .wav files will be saved here
├── main.py          # Python script that does the work
├── README.md        # This file
├── requirements.txt # Python dependencies
└── venv/            # (Optional) Python virtual environment
```

## 🚀 Usage
### 1. Install dependencies
#### ffmpeg
Make sure `ffmpeg` is installed and available in your system PATH:
```bash
# On macOS
brew install ffmpeg

# On Ubuntu
sudo apt install ffmpeg
```

#### figlet (optional)
If you want the fancy ASCII banner:
```bash
# On macOS
brew install figlet

# On Ubuntu
sudo apt install figlet
```

### 2. Set up Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add your `.m4a` files
Place files anywhere inside the `downloads/` directory (subdirectories are supported).

### 4. Run the script
```bash
python main.py
```

Converted `.wav` files will appear in `output/` with the same structure as `downloads/`. 
After conversion, all `.m4a` files (except `.gitkeep`) will be deleted from `downloads/`.

---

## 📦 requirements.txt
```txt
```
*No Python packages needed — `ffmpeg` and `figlet` are system dependencies.*
