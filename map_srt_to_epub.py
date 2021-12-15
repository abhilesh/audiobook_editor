"""
def parse_toc_epub(epub_book):

        '''Subroutine to parse the toc of an epub book'''

        # List to hold the table of contents titles
        toc_titles_list = []

        # Gather the chapter titles from the table of contents
        for toc_el in epub_book.toc:
                if type(toc_el) in [tuple, list, set]:
                        for l1_item in toc_el:
                                if type(l1_item) in [tuple, list, set]:
                                        for l2_item in l1_item:
                                                print(l2_item)
                                                toc_titles_list.append(l2_item.title)
                                else:
                                        toc_titles_list.append(l1_item.title)
                else:
                        toc_titles_list.append(toc_el.title)

        return toc_titles_list
"""


def parse_arguments():

    """Adding flags for more modular conversion"""

    parser = argparse.ArgumentParser()

    parser.add_argument("book_srt", help="Text version of the audiobook")

    # parser.add_argument('-b', '--epub_file', help = 'Epub file of the book')

    parser.add_argument("-o", "--output_file", help="Name of the output file")

    parser.add_argument(
        "-ch",
        "--chapter_heads_only",
        action="store_true",
        help="Extract only Chapter headers such as Chapter 1, Chapter 2 etc...",
    )

    args = parser.parse_args()

    # book_srt = args.book_srt
    # book_epub = args.epub_file
    # chapter_heads_only = args.chapter_heads_only

    return args


# Old working version above, test version below
def parse_toc_epub(epub_book):

    """Subroutine to parse the toc of an epub book"""

    def flatten_toc(toc_list):

        """Subroutine to flatten nested tocs"""

        for toc_el in toc_list:
            if isinstance(toc_el, Iterable) and not isinstance(toc_el, (str, bytes)):
                yield from flatten_toc(toc_el)
            else:
                yield toc_el

    # List to hold the table of content titles
    toc_titles_list = [toc_el.title for toc_el in list(flatten_toc(epub_book.toc))]

    return toc_titles_list


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


def process_toc(book_toc):

    """Subroutine to process the book's toc
    ---------------------------------------
    Convert digits to words"""

    # Dictionary to hold the processed_toc
    toc_processed = []

    for toc_title in book_toc:

        digits_in_title = re.findall(r"\d+", toc_title)

        for digit in digits_in_title:
            toc_title = toc_title.replace(digit, num2words(digit))

        toc_processed.append(toc_title)

    return toc_processed


def map_srt_to_epub(
    book_srt, epub_book=None, output_file=None, chapter_heads_only=False
):

    # Pre-process the srt file
    srt_processed = process_srt(book_srt, chapter_heads_only=chapter_heads_only)

    book_srt_list = srt_processed[0]
    srt_contents_list = srt_processed[1]
    srt_comp_indices = srt_processed[2]

    # print(srt_comp_indices)

    # Look for chapter headers only
    if chapter_heads_only:
        toc_titles_list = ["chapter"]

    elif not chapter_heads_only:
        toc_titles_list = process_toc(parse_toc_epub(book))

    # Initiate containers to hold matches (Why am I using best_match_dict?)
    best_match_dict = {}

    chapter_timestamps = []

    for toc_title in toc_titles_list:

        if chapter_heads_only:

            for srt_el in srt_contents_list:
                if toc_title in srt_el:
                    best_match_index = srt_comp_indices[srt_el]

                    # Index -1 to account for python's way of counting
                    chapter_timestamps.append(
                        (book_srt_list[best_match_index - 1].start, srt_el)
                    )

                    logging.info(srt_el)
                    logging.info(book_srt_list[best_match_index - 1])
                    logging.info("")

                    # best_match_dict.update({srt_el : best_match_index})

            # for toc_el in best_match_dict:

            # best_matches = process.extract(toc_title, srt_contents_list, scorer=fuzz.token_sort_ratio)
            # best_match_indices = [ match.index for match in best_matches ]

            # print(best_matches)

        elif not chapter_heads_only:

            toc_title_key = toc_title.split()[0].lower()

            best_match = process.extractOne(
                toc_title, srt_contents_list, scorer=fuzz.token_set_ratio
            )
            best_match_index = srt_comp_indices[best_match[0]]

            best_match_dict.update({toc_title: best_match_index})

            if toc_title_key in book_srt_list[best_match_index].content:

                chapter_timestamps.append(
                    (book_srt_list[best_match_index].start, toc_title)
                )

                logging.info(toc_title)
                logging.info(book_srt_list[best_match_index])
                logging.info("")

            elif toc_title_key in book_srt_list[best_match_index - 1].content:

                chapter_timestamps.append(
                    (book_srt_list[best_match_index - 1].start, toc_title)
                )

                logging.info(toc_title)
                logging.info(book_srt_list[best_match_index - 1])
                logging.info(book_srt_list[best_match_index])
                logging.info("")

    with open(output_file, "w") as outfile:

        err_chaps = []
        prev_timestamp = srt.srt_timestamp_to_timedelta("00:00:00,000")

        for chapter_el in chapter_timestamps:

            timestamp = srt.timedelta_to_srt_timestamp(chapter_el[0]).replace(",", ".")
            outfile.write(timestamp + " " + string.capwords(chapter_el[1]) + "\n")

            if chapter_el[0] < prev_timestamp:
                err_chaps.append(chapter_el[1])

            prev_timestamp = chapter_el[0]

    with open(output_file.with_suffix(".err"), "w") as err_file:
        for err in err_chaps:
            err_file.write(err + "\n")

    return


if __name__ == "__main__":

    import sys
    import ebooklib
    import srt
    import json
    import datetime
    import logging
    import string
    import re
    import itertools
    import argparse
    from ebooklib import epub

    # Explictly import toc classes for type checking
    from ebooklib.epub import Link, Section
    from pathlib import Path
    from collections import OrderedDict
    from collections.abc import Iterable
    from fuzzywuzzy import process, fuzz
    from num2words import num2words

    # filename = Path(sys.argv[1])
    input_args = parse_arguments()

    filename = Path(input_args.book_srt)
    chapter_heads_only = input_args.chapter_heads_only

    logging.basicConfig(
        filename=filename.with_suffix(".log"),
        filemode="w",
        format="%(message)s",
        level=logging.DEBUG,
    )

    work_dir = Path.cwd() / "work_dir"

    book_srt = srt.parse(filename.with_suffix(".srt").read_text())

    if not chapter_heads_only:
        book = epub.read_epub(filename.with_suffix(".epub"))
    elif chapter_heads_only:
        book = None

    if input_args.output_file == None:
        output_file = filename.with_suffix(".chapters.txt")
    else:
        output_file = None

    map_srt_to_epub(
        book_srt,
        epub_book=book,
        chapter_heads_only=input_args.chapter_heads_only,
        output_file=output_file,
    )
