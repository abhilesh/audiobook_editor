# Script to generate speech-to-text transcriptions for audio files using faster-whisper

import sys
import subprocess
import pysubs2
from pathlib import Path
from faster_whisper import WhisperModel

# Get the filename from the command line
filename = Path(sys.argv[1])
base_dir = filename.parent

print(f"Working on rechapterizing {filename.name}")

print(f"Step 1: Checking for m4b file or converting to m4b.....")

# Check if m4b versions of the file exist
if not filename.with_suffix(".m4b").exists():
    subprocess.run(
        ["m4b-tool", "merge", filename, f"--output-file={filename.with_suffix('.m4b')}"]
    )
else:
    print(f"m4b file already exists for {filename.name}")

print(f"Step 2: Generating speech-to-text maps for m4b file.....")

model_size = "small"

model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, _ = model.transcribe(audio=str(filename))

# to use pysubs2, the argument must be a segment list-of-dicts
results = []
for s in segments:
    segment_dict = {"start": s.start, "end": s.end, "text": s.text}
    results.append(segment_dict)

subs = pysubs2.load_from_whisper(results)
# save srt file
subs.save(filename.with_suffix(".srt"))
# save ass file
subs.save(filename.with_suffix(".ass"))
