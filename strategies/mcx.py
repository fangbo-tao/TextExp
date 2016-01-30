import sys
import bisect
import operator
from utils.utils import load_cube as load_cube
from utils.utils import normalize
import nltk.data
import nltk
import re
from sets import Set

pros = Set(['the', 'a', 'an', 'on', 'and', 'is', 'from', 'for', 'or', 'in', 'of', 'to', 'this', 'that', 'by', 'at'])

def get_stopwords(stopwords_file):
	stopwords = Set()
	with open(stopwords_file, 'r') as f:
		for line in f:
			stopwords.add(line.strip())

	return stopwords


def is_stop_word(sub_tokens, stopwords):

	if sub_tokens[-1] in pros or sub_tokens[0] in pros:
		return True

	for item in sub_tokens:
		if item not in stopwords:
			return False

	return True

def pre_pre_process(raw_text_file, pure_freq_file, stopword_file, threshold=5, minlen=2, maxlen=5):
	doc_phrase_map = {}
	phrase_list = {}
	stopwords = get_stopwords(stopword_file)

	with open(raw_text_file, 'r') as f:
		idx = 0
		for doc in f:
			print idx
			phrase_set = Set()
			#if idx > 500:
			#	break
			doc_phrase_map[idx] = Set()
			doc = doc.lower().replace('\'s ', ' ').replace(' mr. ', ' mr ').replace(' miss. ', ' miss ')
			sents = nltk.sent_tokenize(doc)
			#print '\n'.join(sents)
			for sent in sents:
				matches = re.findall('([a-zA-Z ]+)', sent)
				for match in matches:
					#match = 'hello world I am here'
					tokens = match.strip().split(' ')
					if len(tokens) <= minlen:
						continue
					max_loc = min(len(tokens) - 1, maxlen)
					min_loc = minlen
					for i in range(min_loc, max_loc + 1):
						for j in range(len(tokens) - i + 1):
							sub_tokens = tokens[j:j+i]
							# if sub_tokens[0] in stopwords or sub_tokens[-1] in stopwords:
							# 	continue
							if is_stop_word(sub_tokens, stopwords):
								continue
							phrase = ' '.join(sub_tokens)
							doc_phrase_map[idx].add(phrase)

							if phrase not in phrase_set:
								phrase_list[phrase] = 1 if phrase not in phrase_list else phrase_list[phrase] + 1
							phrase_set.add(phrase)

					# import ipdb
					# ipdb.set_trace()

			print idx
			idx += 1

	filtered_phrase_list = []
	for phrase in phrase_list:
		if phrase_list[phrase] >= threshold:
			filtered_phrase_list.append((phrase, phrase_list[phrase]))
		else:
			print phrase

	#filtered_phrase_list.sort(key=lambda r:r[1], reverse=True)
	all_keys = [r[0] for r in filtered_phrase_list]
	keys_set = Set(all_keys)
	with open(pure_freq_file, 'w+') as g:
		for doc_id, phrases in doc_phrase_map.items():
			doc_phrases = []
			for phrase in phrases:
				if phrase in keys_set:
					doc_phrases.append(phrase)
			phrase_strs = [p + '|1' for p in doc_phrases]
			line = str(doc_id) + ':' + ','.join(phrase_strs) + '\n'
			g.write(line)


def pre_processing(pure_freq_file, unified_file, forward_file):
	phrase_dict = {}
	forward_list = []

	with open(pure_freq_file, 'r') as f:
		for line in f:
			elems = line.strip(' \n').split(':')
			# print line
			tokens = elems[1].split(',')
			phrases_in_doc = []
			for token in tokens:
				phrase = normalize(token.split('|')[0])
				# only keep n-grams
				if ' ' not in phrase:
					continue
				phrase_dict[phrase] = 1 if phrase not in phrase_dict else phrase_dict[phrase] + 1
				phrases_in_doc.append(phrase)

			forward_list.append(phrases_in_doc)

	# sort the forward list by frequency of phrase
	forward_list_true = []
	idx = 0
	for phrases_in_doc in forward_list:
		idx += 1
		print idx
		temp_list = {}
		for phrase in phrases_in_doc:
			occur = phrase_dict[phrase]
			temp_list[phrase] = occur
		
		ranked_list = sorted(temp_list, key=temp_list.get, reverse=False)
		forward_list_true.append(ranked_list)


	with open(unified_file, 'w+') as f:
		for phrase in phrase_dict:
			f.write(phrase + '\t' + str(phrase_dict[phrase]) + '\n')

	with open(forward_file, 'w+') as f:
		for phrases_in_doc in forward_list_true:
			f.write(','.join(phrases_in_doc) + '\n')



def parse_unified_file(unified_file):
	phrase_dict = {}
	with open(unified_file, 'r') as f:
		for line in f:
			tokens = line.split('\t')
			phrase_dict[tokens[0]] = int(tokens[1])

	return phrase_dict


def parse_forward_map(forward_map):
	forward_list = []
	with open(forward_map, 'r') as f:
		for line in f:
			tokens = line.strip(' \n').split(',')
			forward_list.append(tokens)
	return forward_list


def merge_forward_list(phrase_dict, forward_map, selected_docs):
	""" Implement the k-way merge join for VLDB 2010 paper
	"""
	MAX = 1000000000
	MAX_STR = '##DEFAULT_MAX##'
	phrase_dict[MAX_STR] = MAX
	selected_map = [forward_map[index] for index in selected_docs]
	for doc_phr in selected_map:
		doc_phr.append(MAX_STR)


	scale_docs = [(idx, phrase_dict[doc_phr[0]]) for idx, doc_phr in enumerate(selected_map)]
	scale_docs.sort(key=lambda r:r[1])
	# print scale_docs
	keys = [r[1] for r in scale_docs]
	indices_docs = [0 for doc in selected_docs]
	dynamic_phrases = {}

	target_pair = scale_docs.pop(0)
	keys.pop(0)
	while target_pair[1] < MAX:
		doc_id = target_pair[0]
		phrase = selected_map[doc_id][indices_docs[doc_id]]
		dynamic_phrases[phrase] = 1 if phrase not in dynamic_phrases else dynamic_phrases[phrase] + 1
		indices_docs[doc_id] += 1
		# insert into phrase
		phrase = selected_map[doc_id][indices_docs[doc_id]]
		scale_phrase = phrase_dict[phrase]
		pos_ins = bisect.bisect_left(keys, scale_phrase)
		# print keys
		# print scale_phrase
		# print pos_ins
		scale_docs.insert(pos_ins, (doc_id, scale_phrase))
		#print scale_docs
		keys.insert(pos_ins, scale_phrase)
		target_pair = scale_docs.pop(0)
		# print target_pair
		# print scale_docs
		keys.pop(0)

	#print dynamic_phrases['currency controls']
	return dynamic_phrases


def context_score_vldb(dynamic_phrases, phrase_dict, threshold=0):
	""" Context scoring as VLDB 2010
	"""
	for phrase in dynamic_phrases:
		context_score = dynamic_phrases[phrase] / float(phrase_dict[phrase])
		if phrase_dict[phrase] <= threshold:
			dynamic_phrases[phrase] = -1
		else:
			dynamic_phrases[phrase] = context_score



def rank_phrase(unified_file, forward_map_file, cell_file, output_file, n_docs, filtered_cell_str):
	phrase_dict = parse_unified_file(unified_file)
	forward_map = parse_forward_map(forward_map_file)

	cells = load_cube(cell_file)

	for att in cells:
		if att != filtered_cell_str: #'Topic|Sports;Location|Illinois;':
			continue
		print "start processing " + att
		# get all phrasesas
		selected_docs = cells[att]
		dynamic_phrases = merge_forward_list(phrase_dict, forward_map, selected_docs)
		#context_score_vldb(dynamic_phrases, phrase_dict, threshold=5)
		context_score_vldb(dynamic_phrases, phrase_dict)
		sorted_phrase = sorted(dynamic_phrases.items(), key=operator.itemgetter(1), reverse=True)
		with open(output_file, 'w+') as g:
			for pair in sorted_phrase:
				g.write(pair[0] + '\t' + str(pair[1]) + '\n')


if __name__ == "__main__":
	if len(sys.argv) < 3:
		print "1. <usage> prepreprocess [raw text file] [pure freq file] [stopword file]"
		print "2. <usage> preprocess [pure_freq_file] [unfied file] [forward file]"
		print "3. <usage> rank [unified] [forward map] [cube file] [output file] [#docs] [target cell str]"
		sys.exit(-1)

	if sys.argv[1] == 'prepreprocess':
		pre_pre_process(sys.argv[2], sys.argv[3], sys.argv[4])

	elif sys.argv[1] == 'preprocess':
		pre_processing(sys.argv[2], sys.argv[3], sys.argv[4])

	elif sys.argv[1] == 'rank':
		rank_phrase(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], int(sys.argv[6]), sys.argv[7])



