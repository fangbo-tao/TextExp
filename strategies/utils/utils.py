import codecs

def load_simple_measure(data_file):
	doc_phrase_measure = {}
	with codecs.open(data_file, "r", encoding="utf-8") as df:
		for line in df:
			arr = line.strip().split(':')
			doc_index = int(arr[0])
			doc_phrase_measure[doc_index] = {}
			for phrase_measure in arr[1].strip().split(','):
				ph_me_arr = phrase_measure.strip().split('|')
				if len(ph_me_arr) < 2:
					continue
				phrase = ph_me_arr[0]
				measure = float(ph_me_arr[1])

				doc_phrase_measure[doc_index][phrase] = measure

	return doc_phrase_measure


def agg_phrase_cnt(freq_data, selected_doc=None):
	phrase_cnt = {}

	if selected_doc == None:
		for doc_index in freq_data:
			for phrase in freq_data[doc_index]:
				if phrase not in phrase_cnt:
					phrase_cnt[phrase] = 0
				phrase_cnt[phrase] += freq_data[doc_index][phrase]
	else:
		for doc_index in selected_doc:
			for phrase in freq_data[doc_index]:
				if phrase not in phrase_cnt:
					phrase_cnt[phrase] = 0
				phrase_cnt[phrase] += freq_data[doc_index][phrase]

	return phrase_cnt


def agg_phrase_df(freq_data, selected_doc=None):
	phrase_df = {}
	for doc_index in freq_data:
		if selected_doc is not None and doc_index not in selected_doc:
			continue
		for phrase in freq_data[doc_index]:
			if phrase not in phrase_df:
				phrase_df[phrase] = 0

			phrase_df[phrase] += 1

	return phrase_df


def extract_phrases(freq_data, selected_doc):
	phrase_dict = {}
	for doc_index in freq_data:
		if doc_index not in selected_doc:
			continue
		for phrase in freq_data[doc_index]:
			phrase_dict[phrase] = 1

	return phrase_dict


def load_stop_word(stop_word_file):
	stop_words = {}
	with open(stop_word_file, 'r') as f:
		for line in f:
			word = line.strip()
			stop_words[word] = 1

	return stop_words

def load_frequent_patterns(freq_pattern_file):
	word_seq_cnt = {}
	with codecs.open(freq_pattern_file, "r", encoding="utf-8") as f:
		for line in f:
			arr = line.strip().split(",")
			if len(arr) < 2:
				continue
			word_seq_cnt[arr[0]] = int(arr[1])

	return word_seq_cnt

def save_dict_list(dict_list, file_name):
	with codecs.open(file_name, "w+", encoding="utf-8") as f:
		for k in dict_list:
			indexed_vals = []
			cnt = 0
			for v in dict_list[k]:
				indexed_val = "{0}:{1}".format(cnt, v)
				indexed_vals.append(indexed_val)

			wline = u"{0}\t{1}\n".format(k, " ".join(indexed_vals))
			f.write(wline)

def load_cube(cube_file):
	selected_docs = {}
	with codecs.open(cube_file, "r", encoding='utf-8') as cf:
		for line in cf:
			arr = line.strip().split(':')
			att = arr[0]
			doc_list_str = arr[1].strip().split(",")
			doc_list = [int(d) for d in doc_list_str]

			selected_docs[att] = doc_list

	return selected_docs

def load_context(context_file):
	context_docs = {}
	with codecs.open(context_file, "r", encoding='utf-8') as cf:
		for line in cf:
			arr = line.strip().split(':')
			att = arr[0]
			context_docs[att] = {}
			doc_lists = arr[1].strip().split(";")
			for doc_list in doc_lists:
				tokens = doc_list.strip().split('|')
				cell_name = tokens[0]
				docs_str = tokens[1]
				doc_list_str = docs_str.strip().split(",")
				doc_list = [int(d) for d in doc_list_str]
				context_docs[att][cell_name] = doc_list

	return context_docs

def load_unified_list(unified_file):
	unified_list = {}
	with codecs.open(unified_file, "r", encoding='utf-8') as cf:
		for line in cf:
			arr = line.strip().split(',')
			phrase = normalize(arr[0])
			score = arr[1]
			unified_list[phrase] = score
	return unified_list   

def normalize(word):
	word = word.lower()
	result = []
	for i in xrange(len(word)):
		if word[i].isalpha() or word[i] == '\'':
			result.append(word[i])
		else:
			result.append(' ')
	word = ''.join(result);
	return ' '.join(word.split())


def normalize_feature(feature_dict):
	max_val = max(feature_dict.values())
	if max_val == 0:
		max_val = 1.0
	for f in feature_dict:
		feature_dict[f] /= max_val


def load_cell_top_phrases(top_phrase_file):
	'''
	Load the cell top phrase list
	'''
	top_phrases = {}
	with codecs.open(top_phrase_file, "r", encoding='utf-8') as f:
		for line in f:
			tokens = line.strip('\n').split(':')
			cell_str = tokens[0]
			phrases = tokens[1].split(',')
			top_phrases[cell_str] = phrases
	return top_phrases


def load_raw_text(raw_text_file):
	raw_text_dict = {}
	with codecs.open(raw_text_file, "r", encoding='utf-8') as raw:
		idx = 0
		for line in raw:
			raw_text_dict[idx] = line
			idx += 1
	return raw_text_dict

