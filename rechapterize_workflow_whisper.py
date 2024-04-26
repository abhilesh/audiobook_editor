# Script to generate speech-to-text transcriptions for audio files

import sys
import subprocess
import whisper
from whisper.utils import get_writer
from pathlib import Path

# Get the filename from the command line
filename = Path(sys.argv[1])
base_dir = filename.parent

print(f"Working on rechapterizing {filename.name}")

print(f"Step 1: Checking for m4b file or converting to m4b.....")

# Merge the mp3 files into a single m4b file

# Check if m4b versions of the file exist
if not filename.with_suffix(".m4b").exists():
    subprocess.run(
        ["m4b-tool", "merge", filename, f"--output-file={filename.with_suffix('.m4b')}"]
    )
else:
    print(f"m4b file already exists for {filename.name}")

print(f"Step 2: Generating speech-to-text maps for m4b file.....")

model = whisper.load_model("small")

result = model.transcribe(str(filename.with_suffix(".m4b")), verbose=False)

srt_writer = get_writer("srt", base_dir)
srt_writer(result, filename.with_suffix(".srt"))
