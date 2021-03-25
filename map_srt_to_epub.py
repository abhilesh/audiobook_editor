

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
						toc_titles_list.append(l2_item.title)
				else:
					toc_titles_list.append(l1_item.title)
		else:
			toc_titles_list.append(toc_el.title)

	return toc_titles_list


def process_srt(book_srt):

	'''Subroutine to process the book srt into processable chunks'''

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
			comp_srt_content = ' '.join([book_srt_list[index-2].content,
										book_srt_list[index-1].content,
										book_srt_list[index].content])

			srt_contents_list.append(comp_srt_content)
			srt_comp_indices.update({comp_srt_content : index})

	return book_srt_list, srt_contents_list, srt_comp_indices


def process_toc(book_toc):

	'''Subroutine to process the book's toc
	---------------------------------------
	Convert digits to words'''

	# Dictionary to hold the processed_toc
	toc_processed = []

	for toc_title in book_toc:

		digits_in_title = re.findall(r'\d+', toc_title)

		for digit in digits_in_title:
			toc_title = toc_title.replace(digit, num2words(digit))

		toc_processed.append(toc_title)

	return toc_processed


def map_srt_to_epub(epub_book, book_srt, chapters_file=None):

	toc_titles_list = process_toc(parse_toc_epub(book))
	srt_processed = process_srt(book_srt)

	print(toc_titles_list)

	book_srt_list = srt_processed[0]
	srt_contents_list = srt_processed[1]
	srt_comp_indices = srt_processed[2]

	best_match_dict = {}

	chapter_timestamps = []

	for toc_title in toc_titles_list:

		toc_title_key = toc_title.split()[0].lower()

		best_match = process.extractOne(toc_title, srt_contents_list, scorer=fuzz.token_set_ratio)
		best_match_index = srt_comp_indices[best_match[0]]

		best_match_dict = {toc_title : best_match_index}

		if toc_title_key in book_srt_list[best_match_index].content:

			chapter_timestamps.append((book_srt_list[best_match_index].start, toc_title))

			logging.info(toc_title)
			logging.info(book_srt_list[best_match_index])
			logging.info('')

		elif toc_title_key in book_srt_list[best_match_index-1].content:

			chapter_timestamps.append((book_srt_list[best_match_index-1].start, toc_title))

			logging.info(toc_title)
			logging.info(book_srt_list[best_match_index-1])
			logging.info(book_srt_list[best_match_index])
			logging.info('')

	with open(chapters_file, 'w') as outfile:
		
		err_chaps = []
		prev_timestamp = srt.srt_timestamp_to_timedelta('00:00:00,000')

		for chapter_el in chapter_timestamps:
			
			timestamp = srt.timedelta_to_srt_timestamp(chapter_el[0]).replace(',', '.')
			outfile.write(timestamp + ' ' + string.capwords(chapter_el[1]) + '\n')

			if chapter_el[0] < prev_timestamp:
				err_chaps.append(chapter_el[1])

			prev_timestamp = chapter_el[0]		


	with open(chapters_file.with_suffix('.err'), 'w') as err_file:
		for err in err_chaps:
			err_file.write(err + '\n')


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
	from ebooklib import epub
	from pathlib import Path
	from collections import OrderedDict
	from fuzzywuzzy import process, fuzz
	from num2words import num2words

	filename = sys.argv[1] 

	logging.basicConfig(filename=f"{filename}.log", filemode='w', format='%(message)s', level=logging.DEBUG)

	book = epub.read_epub(Path(Path.cwd() / f"{filename}.epub"))
	book_srt = srt.parse(Path(Path.cwd() / f"{filename}.srt").read_text())

	map_srt_to_epub(book, book_srt, chapters_file=Path(Path.cwd()/f'{filename}.chapters.txt'))

