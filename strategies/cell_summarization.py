import sys
from sklearn import cluster, datasets
import nltk.data
import nltk
import numpy as np
from sets import Set
import re
import codecs


def get_sentences(raw_text):
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	fp = open(raw_text)
	data = fp.read().decode('utf-8')

	callback = lambda pat: '. ' + pat.group(1)[1:]
	data = re.sub(r'(\.[A-Z])', callback, data)
	data = re.sub(r'(\.\[[A-Z])', callback, data)

	with open('temp_china_business.txt', 'w+') as g:
		g.write(data.encode('utf-8'))

	return tokenizer.tokenize(data)

def get_phrases(phrase_list_file):
	ps = []
	with codecs.open(phrase_list_file, 'r', encoding='utf-8') as f:
		for line in f:
			ps.append('%s' % line.strip())
	return ps

def get_stopwords(stopwords_file):
	stopwords = Set()
	with open(stopwords_file, 'r') as f:
		for line in f:
			stopwords.add(line.strip())

	return stopwords


def get_valid_sentences(sentences, top_phrases):
	valid_sentences = {}
	for sentence in sentences:
		sentence = sentence.lower()
		for phrase in top_phrases:
			if phrase in sentence:
				if sentence not in valid_sentences:
					valid_sentences[sentence] = Set()
				valid_sentences[sentence].add(phrase)
	return valid_sentences


def get_mutual_score(sent_1, sent_2, list_1, list_2, tokens_1, tokens_2, stopwords):
	factor_phrase = 5
	factor_word = 1
	num_phrase = 0
	num_word = 1
	for phrase in list_2:
		if phrase in list_1:
			num_phrase += 1

	for token in tokens_2:
		if token.isalpha() and token not in stopwords and token in tokens_1:
			num_word += 1

	# if sent_1 != sent_2 and num_phrase > 1:
	# 	print sent_1
	# 	print sent_2
	# 	print list_1
	# 	print list_2
	# 	print num_phrase
	# 	print num_word

	score = factor_phrase * num_phrase + factor_word * num_word
	if sent_1 != sent_2 and score > 20:
		print sent_1
		print sent_2

	return score


def get_affinity_matrix(valid_sentences, stopwords):
	sentences = valid_sentences.keys()
	sent_tokens = {}
	for sentence in sentences:
		sent_tokens[sentence] = Set(nltk.word_tokenize(sentence))

	cnt = len(sentences)
	X = np.random.rand(cnt, cnt)

	for idx_1, sentence_1 in enumerate(sentences):
		print idx_1
		for idx_2, sentence_2 in enumerate(sentences):
			if idx_2 < idx_1:
				continue
			score = get_mutual_score(sentence_1, sentence_2, 
				valid_sentences[sentence_1], valid_sentences[sentence_2],
				sent_tokens[sentence_1], sent_tokens[sentence_2], stopwords)
			X[idx_1, idx_2] = score
			X[idx_2, idx_1] = score

	return sentences, X




def labels_spectral(affinity, n_cluster):
	# X = np.random.rand(10, 10)
	# X = np.tril(X) + np.tril(X, -1).T
	labels = cluster.spectral_clustering(affinity, n_clusters=n_cluster, eigen_solver='arpack')
	return labels

def get_center_idx(sub_matrix, size):
	max_idx = -1
	max_affinity = -1
	for i in range(0, size):
		sum_affinity = 0
		for j in range(0, size):
			if i != j:
				sum_affinity += sub_matrix[i, j]
		if sum_affinity > max_affinity:
			max_affinity = sum_affinity
			max_idx = i
	return max_idx


# data = "shift the [economy] away from a focus on [manufacturing].[China's economy] is set to grow this year at its weakest pace since, as flagging [foreign and domestic] [demand] weighs on exports and [factory production].A [slowdown] in inve"
# callback = lambda pat: '. ' + pat.group(1)[1:]
# data = re.sub(r'(\.[A-Z])', callback, data)
# data = re.sub(r'(\.\[[A-Z])', callback, data)
# print data


def gen_sent(raw_text, ph_file, stop_words, event_id):

	# if len(sys.argv) != 5:
	#     print '[usage] <raw_text> <top phrases file> <stop words> <cluster number>'
	#     sys.exit(-1)

	n_clusters = 3


	sentences = get_sentences(raw_text)
	top_phrases = get_phrases(ph_file)
	stopwords = get_stopwords(stop_words)

	valid_sentences = get_valid_sentences(sentences, top_phrases)
	print len(valid_sentences)
	total_sent = 'valid sentence # : ' + str(len(valid_sentences))

	sentences, X = get_affinity_matrix(valid_sentences, stopwords)

	lable_num = n_clusters
	labels = labels_spectral(X, lable_num)
	print labels

	fn = '../data/attack/result/' + str(event_id) + '.sent'
	with codecs.open(fn, 'w', encoding='utf-8') as f:
		for i in range(0, lable_num):
			group_idxes = []
			for idx, label in enumerate(labels):
				if label == i:
					group_idxes.append(idx)
			num_in_label = len(group_idxes)
			print num_in_label
			rows = np.array(group_idxes, dtype=np.intp)
			columns = np.array(group_idxes, dtype=np.intp)
			sub_matrix = X[rows[:, np.newaxis], columns]
			max_idx = get_center_idx(sub_matrix, num_in_label)
			sentence = sentences[group_idxes[max_idx]]
			f.write(sentence + '\n')

		#sub_matrix = np.random.rand(num_in_label, num_in_label)


if __name__ == "__main__":
	for e_id in xrange(1, 52):
		if e_id == 46:
			continue
		raw_text = '../data/attack/result/' + str(e_id) + '.txt'
		ph_file = '../data/attack/result/' + str(e_id) + '.ph'
		stop_words = '../data/attack/stopwords.txt'

		print 'currently generating sentences for event ' + str(e_id)
		gen_sent(raw_text, ph_file, stop_words, e_id)




