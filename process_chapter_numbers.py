def process_srt(book_srt, chapter_heads_only=False):

    """Subroutine to process the book srt into processable chunks"""

    if not isinstance(book_srt, list):
        book_srt_list = list(book_srt)
    elif isinstance(book_srt, list):
        book_srt_list = book_srt

    # List to process the srt data into chunks for subsequent matching
    srt_contents_list = []

    # Dictionary to hold the content: index mapping for comp_srt_content
    srt_comp_indices = {}

    for index, srt_el in enumerate(book_srt_list, start=1):

        if index not in [1, len(book_srt_list)]:
            # Process as 1stack if only chapter heads are found
            if chapter_heads_only:
                comp_srt_content = book_srt_list[index - 1].content

                srt_contents_list.append(comp_srt_content)
                srt_comp_indices.update({comp_srt_content: index})
            # Consolidate the subtitles into rolling triplets for longer title matching
            elif not chapter_heads_only:
                comp_srt_content = " ".join(
                    [
                        book_srt_list[index - 2].content,
                        book_srt_list[index - 1].content,
                        book_srt_list[index].content,
                    ]
                )

                srt_contents_list.append(comp_srt_content)
                srt_comp_indices.update({comp_srt_content: index})

    return book_srt_list, srt_contents_list, srt_comp_indices


def find_chapter_marks(book_srt, chapter_heads_only=True):

    # Pre-process the srt file
    srt_processed = process_srt(book_srt, chapter_heads_only=chapter_heads_only)

    book_srt_list = srt_processed[0]
    srt_contents_list = srt_processed[1]
    srt_comp_indices = srt_processed[2]

    chapter_timestamps = []

    for srt_el in srt_contents_list:
        if "chapter" in srt_el.split(" ")[0]:
            best_match_index = srt_comp_indices[srt_el]

            # Index -1 to account for python's way of counting
            chapter_timestamps.append(
                (book_srt_list[best_match_index - 1].start, srt_el)
            )

    for chapter_el in chapter_timestamps:

        timestamp = srt.timedelta_to_srt_timestamp(chapter_el[0]).replace(",", ".")
        title_parts = chapter_el[1].split()

        chapter_number = " ".join(title_parts[1:])

        try:
            chapter_title = (
                string.capwords(title_parts[0])
                + " "
                + str(w2n.word_to_num(chapter_number))
            )

            print(f"{timestamp} {chapter_title}")

        except ValueError:
            pass

    return chapter_timestamps


if __name__ == "__main__":

    import sys
    import srt
    import string
    from pathlib import Path
    from word2number import w2n

    filename = Path(sys.argv[1])

    book_srt = srt.parse(filename.with_suffix(".srt").read_text())

    chapter_timestamps = find_chapter_marks(book_srt=book_srt)

