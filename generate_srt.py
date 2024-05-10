#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
from tqdm import tqdm
import sys
import os
import subprocess
import srt
import json
import datetime
import time
import soundfile as sf


def setup_vosk():
    SetLogLevel(-1)

    if not os.path.exists("model"):
        print(
            "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder."
        )
        exit(1)

    sample_rate = 16000
    model = Model("model")
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    return rec, sample_rate


def setup_ffmpeg(ab_file, sample_rate):

    process = subprocess.Popen(
        [
            "ffmpeg",
            "-loglevel",
            "quiet",
            "-i",
            ab_file,
            "-ar",
            str(sample_rate),
            "-ac",
            "1",
            "-f",
            "s16le",
            "-",
        ],
        stdout=subprocess.PIPE,
    )

    return process


def transcribe(ab_file, rec, process):

    WORDS_PER_LINE = 7
    results = []
    subs = []

    # Get the total duration of the audio file
    # f = sf.SoundFile(ab_file)
    # tot_duration = len(f) / f.samplerate

    # pbar = tqdm(total=tot_duration, desc="Transcribing", unit="block")
    # N = 100  # adjust this based on your needs
    # data_length = 0

    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = rec.Result()
            results.append(result)
            # data_length += len(data)
            # if data_length >= N * 10000:  # update the progress bar every N blocks
            #    pbar.update(data_length / 2 / f.samplerate)  # 2 bytes per sample
            #    data_length = 0  # reset the data length

    # if data_length > 0:  # update the progress bar for the last few blocks
    #    pbar.update(data_length / 2 / f.samplerate)  # 2 bytes per sample

    results.append(rec.FinalResult())

    for i, res in enumerate(results):
        jres = json.loads(res)
        if not "result" in jres:
            continue
        words = jres["result"]
        for j in range(0, len(words), WORDS_PER_LINE):
            line = words[j : j + WORDS_PER_LINE]
            s = srt.Subtitle(
                index=len(subs),
                content=" ".join([l["word"] for l in line]),
                start=datetime.timedelta(seconds=line[0]["start"]),
                end=datetime.timedelta(seconds=line[-1]["end"]),
            )
            subs.append(s)

    # pbar.close()

    return subs


def main(input_file):
    rec, sample_rate = setup_vosk()
    process = setup_ffmpeg(input_file, sample_rate)
    start_time = time.time()
    with open(input_file.with_suffix(".srt"), "w") as srt_outfile:
        srt_outfile.write(srt.compose(transcribe(input_file, rec, process)))
    end_time = time.time()
    print(f"Transcription took {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Transcribe .wav audio file to .srt subtitle file."
    )
    parser.add_argument("input_file", type=str, help="Input .wav audio file.")

    args = parser.parse_args()

    main(args.input_file)
