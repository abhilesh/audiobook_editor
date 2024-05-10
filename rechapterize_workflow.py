#!/usr/bin/env python3

__author__ = "Abhilesh Dhawanjewar"
__version__ = "0.1.0"

import shutil
import subprocess
import sys
import time
from pathlib import Path


def check_required_tools():
    """
    Check if the required tools ("m4b-tool" and "ffmpeg") are installed.
    If a tool is not installed, print a message and exit the script.
    """

    tools = ["m4b-tool", "ffmpeg"]
    for tool in tools:
        if shutil.which(tool) is None:
            print(f"{tool} is not installed. Please install it to proceed.")
            sys.exit(1)


def merge_mp3_files(ab_file):
    """
    Merge the mp3 files into a single m4b file.
    If the m4b file already exists, do nothing.
    """

    if not ab_file.with_suffix(".m4b").exists():
        subprocess.run(
            [
                "m4b-tool",
                "merge",
                ab_file,
                f"--output-file={ab_file.with_suffix('.m4b')}",
            ]
        )


def convert_m4b_to_wav(ab_file):
    """
    Convert the m4b file to a wav file using ffmpeg.
    """
    if not ab_file.with_suffix(".wav").exists():
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                f"{ab_file.with_suffix('.m4b')}",
                "-ar",
                "16000",
                "-ac",
                "1",
                f"{ab_file.with_suffix('.wav')}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def generate_speech_to_text_maps(ab_file):
    """
    Generate speech-to-text maps for the wav file.
    If the srt file already exists, do nothing.
    """

    if not ab_file.with_suffix(".srt").is_file():
        generate_srt.main(ab_file.with_suffix(".wav"))


def identify_chapter_timestamps(ab_file):
    """
    Identify chapter timestamps in the audiobook using the map_srt_to_epub script.
    """

    map_srt_to_epub.main(ab_file)


def main(ab_file):
    """
    Main function to run the rechapterizing workflow.
    """

    check_required_tools()

    print(f"Working on rechapterizing {ab_file}")

    steps = [
        ("Merging mp3 files into m4b file", merge_mp3_files),
        ("Converting m4b file to wav file", convert_m4b_to_wav),
        ("Generating speech-to-text maps for wav file", generate_speech_to_text_maps),
        (
            "Identifying chapter timestamps in the audiobook",
            identify_chapter_timestamps,
        ),
    ]

    for i, (description, function) in enumerate(steps, start=1):
        print(f"Step {i}: {description} .....")
        start_time = time.time()
        function(ab_file)
        end_time = time.time()
        elapsed_time = end_time - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, _ = divmod(remainder, 60)
        print(f"Step {i} took {int(hours)} hours and {int(minutes)} minutes")


if __name__ == "__main__":

    import argparse
    import generate_srt
    import map_srt_to_epub

    parser = argparse.ArgumentParser(
        description="Rechapterize an audiobook by identifying chapter timestamps."
    )
    parser.add_argument("ab_file", help="The audiobook filename")
    args = parser.parse_args()

    main(Path(args.ab_file))
