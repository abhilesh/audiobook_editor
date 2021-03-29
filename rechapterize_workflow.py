#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path

filename = Path(sys.argv[1])

vosk_srt_path = Path.cwd() / 'vosk-api' / 'python' / 'example'

print(f"Working on rechapterizing {filename}")

print(f"Step 1: Merging mp3 files into m4b file .....")

# Merge the mp3 files into a single m4b file

# Check if m4b versions of the file exist
if not filename.with_suffix('.m4b'):
	subprocess.run(['m4b-tool', 'merge', filename,
					f"--output-file={filename.with_suffix('.m4b')}"])

print(f"Step 2: Converting m4b file to wav file .....")

# Convert the m4b file to wav
subprocess.run(['ffmpeg', '-i', 
				f"{filename.with_suffix('.m4b')}", 
				'-ar', '16000',
				'-ac', '1',
				f"{filename.with_suffix('.wav')}"])

print(f"Step 3: Generating speech-to-text maps for wav file .....")

srt_outfile = open(filename.with_suffix('.srt'), 'w')
subprocess.call(['python', f"{vosk_srt_path / 'test_srt.py'}", f"{filename.with_suffix('.wav')}"], stdout=srt_outfile)

print(f"Step 4: Identifying chapter timestamps in the audiobook .....")

subprocess.call(['python', 'map_srt_to_epub.py', f"{filename}"])
