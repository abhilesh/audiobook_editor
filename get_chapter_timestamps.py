import re
import argparse
from word2number import w2n  # Import the word2number library


def parse_srt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    results = []
    for i in range(1, len(lines)):
        # Check if the current line contains "chapter" (case-insensitive)
        if re.search(r"\bchapter\b", lines[i], re.IGNORECASE):
            # Get the line above the "chapter" line
            previous_line = lines[i - 1].strip()

            # Find the timestamp in the line above
            timestamp_match = re.search(r"(\d{2}:\d{2}:\d{2},\d{3})", previous_line)
            if timestamp_match:
                # Extract the timestamp and replace ',' with '.'
                timestamp = timestamp_match.group(1).replace(",", ".")

                # Capitalize "Chapter" and convert numerical words to numbers
                chapter_line = lines[i].strip().capitalize()
                chapter_line = re.sub(
                    r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(\s(one|two|three|four|five|six|seven|eight|nine))?\b",
                    lambda match: str(w2n.word_to_num(match.group(0))),
                    chapter_line,
                    flags=re.IGNORECASE,
                )
                results.append((timestamp, chapter_line))

    return results


# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse an SRT file to find chapter timestamps."
    )
    parser.add_argument("srt_file", type=str, help="Path to the SRT file")
    args = parser.parse_args()

    chapter_timestamps = parse_srt(args.srt_file)

    for timestamp, chapter_line in chapter_timestamps:
        print(f"{timestamp} {chapter_line}")
