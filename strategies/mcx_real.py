from utils.utils import agg_phrase_cnt
from utils.utils import agg_phrase_df
from utils.utils import normalize
import sys
import bisect
import operator
from utils.utils import load_cube as load_cube
from utils.utils import normalize
import nltk.data
import nltk
import re
from sets import Set
import codecs
import math

pros = Set(['the', 'a', 'an', 'on', 'and', 'is', 'from', 'for', 'or', 'in', 'of', 'to', 'this', 'that', 'by', 'at'])


class MCX:

	def parse_unified_file(self, unified_file):
		phrase_dict = {}
		with open(unified_file, 'r') as f:
			for line in f:
				tokens = line.split('\t')
				phrase_dict[tokens[0]] = int(tokens[1])

		return phrase_dict


	def parse_forward_map(self, forward_map):
		forward_list = []
		with open(forward_map, 'r') as f:
			for line in f:
				tokens = line.strip(' \n').split(',')
				forward_list.append(tokens)
		return forward_list

	def merge_forward_list(self, phrase_dict, forward_map, selected_docs):
		""" Implement the k-way merge join for VLDB 2010 paper
		"""
		MAX = 1000000000
		MAX_STR = '##DEFAULT_MAX##'
		phrase_dict[MAX_STR] = MAX
		selected_map = [forward_map[index] for index in selected_docs]
		for doc_phr in selected_map:
			if len(doc_phr) == 0 or doc_phr[0] == '':
				# print doc_phr
				doc_phr.remove('')
				doc_phr.append(MAX_STR)
			else:
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


	def context_score_vldb(self, dynamic_phrases, phrase_dict, threshold=0, count_thres=1):
		""" Context scoring as VLDB 2010
		"""
		for phrase in dynamic_phrases:
			context_score = dynamic_phrases[phrase] / float(phrase_dict[phrase])
			if phrase_dict[phrase] <= threshold:
				dynamic_phrases[phrase] = -1
			elif dynamic_phrases[phrase] < count_thres:
				dynamic_phrases[phrase] = -1
			else:
				dynamic_phrases[phrase] = context_score

	def compute(self, selected_docs):
		dynamic_phrases = self.merge_forward_list(self.phrase_dict, self.forward_map, selected_docs)
		self.context_score_vldb(dynamic_phrases, self.phrase_dict)
		sorted_phrase = sorted(dynamic_phrases.items(), key=operator.itemgetter(1), reverse=True)
		return sorted_phrase[:500]


	def __init__(self, unified_file, forward_map_file):
		self.phrase_dict = self.parse_unified_file(unified_file)
		self.forward_map = self.parse_forward_map(forward_map_file)


mcx = None

def point_query(selected_docs, param=None):
	'''
	-- param --
		BASIC: use MCX phrase generator
		SEG: use segphrase as the candidates
	'''
	print 'size of selected'
	print len(selected_docs)
	global mcx
	if param == 'BASIC':
		unified_file = 'data/mcx/mcx_unified_basic.txt'
		forward_map_file = 'data/mcx/forward_map_basic.txt'
	elif param == 'SEG':
		unified_file = 'data/mcx/mcx_unified_sp.txt'
		forward_map_file = 'data/mcx/forward_map_sp.txt'

	if mcx == None:
		mcx = MCX(unified_file, forward_map_file)

	return mcx.compute(selected_docs)


