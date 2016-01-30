from utils.utils import agg_phrase_cnt
from utils.utils import agg_phrase_df
from utils.utils import normalize
from heapq import heappush, heappop, heappushpop, nsmallest, nlargest
import codecs
import math
import ast
import ipdb


class OLAPORP:

	def bm25_df_paper(self, df, max_df, tf, dl, avgdl, k=1.2, b=0.5, multiplier=3):
		score = tf * (k + 1) / (tf + k * (1 - b + b * (dl / avgdl)))
		df_factor = math.log(1 + df, 2) / math.log(1 + max_df, 2)
		score *= df_factor
		score *= multiplier
		return score


	def softmax_paper(self, score_list):
		# normalization of exp
		exp_sum = 1
		for score in score_list:
			exp_sum += math.exp(score)

		exp_list = []
		for score in score_list:
			normal_value = math.exp(score) / exp_sum
			exp_list.append(normal_value)
		return exp_list



	def compute_tfidf(self):
		scores = {}

		sum_self = self.sum_cnt
		num_context_cells = len(self.sum_cnt_context) + 1
		
		for phrase in self.phrase_cnt:
			
			tf = self.phrase_cnt[phrase]
			num_super_cell = 1
			for phrase_group, phrase_values in self.phrase_cnt_context.items():
				if phrase in phrase_values:
					num_super_cell += 1
			idf = math.log(num_context_cells / float(num_super_cell), 2)

			score = tf * idf
			scores[phrase] = score

		ranked_list = [(phrase, scores[phrase]) for phrase in sorted(scores, key=scores.get, reverse=True)]
		return ranked_list


	def compute(self, score_type='ALL'):
		'''
		-- score_type --
			ALL: all three factors
			POP: only popularity
			DIS: only distinctive
			INT: only integrity
			NOPOP: no populairty
			NODIS: no distinctive
			NOINT: no integrity

		'''
		scores = {}
		multiplier = 1

		
		sum_self = self.sum_cnt
		num_context_cells = len(self.sum_cnt_context) + 1
		total_sum = sum(self.sum_cnt_context.values()) + sum_self
		avgdl = total_sum / float(num_context_cells)

		# method 1
		for phrase in self.phrase_cnt:
			lower_phrase = phrase.lower()
			score = 1
			nor_phrase = normalize(lower_phrase)
			self_cnt = self.phrase_cnt[phrase]
			self_df = self.phrase_df[phrase]
			
			group = [(self_df, self.max_df, self_cnt, sum_self)]

			self.context_groups[phrase] = []
			for phrase_group, phrase_values in self.phrase_cnt_context.items():
				context_df = self.phrase_df_context[phrase_group].get(phrase, 0)
				sum_context = self.sum_cnt_context[phrase_group]
				context_cnt = phrase_values.get(phrase, 0)
				maxdf_context = self.max_df_context[phrase_group]

				if (context_cnt > 0):
					group.append((context_df, maxdf_context, context_cnt, sum_context))
					self.context_groups[phrase].append((context_df, maxdf_context, context_cnt, sum_context))
				
			score_list = []
			for record in group:
				score_list.append(self.bm25_df_paper(record[0], record[1], record[2], record[3], avgdl))
			distinct = self.softmax_paper(score_list)[0]
			
			# score_list = map(prettyfloat, score_list)
			# log_str = lower_phrase.encode('utf-8') + ':' + str(prettyfloat(score)) + '\t' +  str(group) +  '\t' + str(score_list) + '\n'
			# log_strs[lower_phrase] = log_str
			# log_scores[lower_phrase] = score
			# distinct = score
			popularity = math.log(1 + self_df, 2)
			try:
				integrity = float(self.global_scores[nor_phrase])
			except:
				integrity = 0.8

			if score_type == 'ALL':
				score = distinct * popularity * integrity
			elif score_type == 'POP':
				score = popularity
			elif score_type == 'DIS':
				score = distinct
			elif score_type == 'INT':
				score = integrity
			elif score_type == 'NOPOP':
				score = distinct * integrity
			elif score_type == 'NODIS':
				score = popularity * integrity
			elif score_type == 'NOINT':
				score = popularity * distinct
			else:
				score = 0

			scores[phrase] = score

		ranked_list = [(phrase, scores[phrase]) for phrase in sorted(scores, key=scores.get, reverse=True)]
		
		print 'OLAPORP DONE'
		return ranked_list


	# added for exploration
	def update_computing(self, score_type='ALL'):
		scores = {}
		multiplier = 1

		sum_self = self.sum_cnt
		num_context_cells = len(self.sum_cnt_context) + 1
		total_sum = sum(self.sum_cnt_context.values()) + sum_self
		avgdl = total_sum / float(num_context_cells)

		# method 1
		for phrase in self.phrase_cnt:
			lower_phrase = phrase.lower()
			score = 1
			nor_phrase = normalize(lower_phrase)
			self_cnt = self.phrase_cnt[phrase]
			self_df = self.phrase_df[phrase]
			

			group = list(self.context_groups[phrase])

			group.append((self_df, self.max_df, self_cnt, sum_self))

			score_list = []
			for record in group:
				score_list.append(self.bm25_df_paper(record[0], record[1], record[2], record[3], avgdl))
			distinct = self.softmax_paper(score_list)[-1]
			
			
			# score_list = map(prettyfloat, score_list)
			# log_str = lower_phrase.encode('utf-8') + ':' + str(prettyfloat(score)) + '\t' +  str(group) +  '\t' + str(score_list) + '\n'
			# log_strs[lower_phrase] = log_str
			# log_scores[lower_phrase] = score
			# distinct = score
			popularity = math.log(1 + self_df, 2)
			try:
				integrity = float(self.global_scores[nor_phrase])
			except:
				integrity = 0.8

			if score_type == 'ALL':
				score = distinct * popularity * integrity
			elif score_type == 'POP':
				score = popularity
			elif score_type == 'DIS':
				score = distinct
			elif score_type == 'INT':
				score = integrity
			elif score_type == 'NOPOP':
				score = distinct * integrity
			elif score_type == 'NODIS':
				score = popularity * integrity
			elif score_type == 'NOINT':
				score = popularity * distinct
			else:
				score = 0

			scores[phrase] = score

		ranked_list = [(phrase, scores[phrase]) for phrase in sorted(scores, key=scores.get, reverse=True)]
		self.ranked_list = ranked_list
		
		print 'OLAPORP DONE'
		return ranked_list


	# added for exploration
	def update_selected_docs(self, freq_data, selected_docs, phrases=[]):
		if not phrases:
			self.selected_docs = selected_docs
			self.phrase_cnt = agg_phrase_cnt(freq_data, selected_docs)
			self.phrase_df = agg_phrase_df(freq_data, selected_docs)
			if len(self.phrase_df) > 0:
				self.max_df = max(self.phrase_df.values())
			else:
				self.max_df = 0
			self.self_dc = len(selected_docs)
			self.sum_cnt = sum(self.phrase_cnt.values())
			self.ranked_list = []


	def __init__(self, freq_data, selected_docs, context_doc_groups, global_scores):
		print 'start query'
		self.selected_docs = selected_docs
		self.phrase_cnt = agg_phrase_cnt(freq_data, selected_docs)
		self.phrase_df = agg_phrase_df(freq_data, selected_docs)
		self.phrase_cnt_context = {}
		self.phrase_df_context = {}
		if len(self.phrase_df) > 0:
			self.max_df = max(self.phrase_df.values())
		else:
			self.max_df = 0
		self.max_df_context = {}
		self.dc_context = {}
		self.self_dc = len(selected_docs)
		self.sum_cnt = sum(self.phrase_cnt.values())
		self.sum_cnt_context = {}
		self.global_scores = global_scores
		for group, docs in context_doc_groups.items():
			self.phrase_cnt_context[group] = agg_phrase_cnt(freq_data, docs)
			self.phrase_df_context[group] = agg_phrase_df(freq_data, docs)
			if len(self.phrase_df_context[group]) > 0:
				self.max_df_context[group] = max(self.phrase_df_context[group].values())
			else:
				self.max_df_context[group] = 0
			self.dc_context[group] = len(docs)
			self.sum_cnt_context[group] = sum(self.phrase_cnt_context[group].values())

		# added for exploration
		self.context_groups = {}
		self.ranked_list = []


def point_query(freq_data, selected_docs, context_doc_groups, global_scores, score_type):
	algorithm = OLAPORP(freq_data, selected_docs, context_doc_groups, global_scores)
	if score_type == 'TFIDF':
		return algorithm.compute_tfidf()
	else:
		return algorithm.compute(score_type), algorithm
	
	# algorithm = OLAPORP_FAKE(freq_data, selected_docs, global_scores)
	# import time
	# trailNum = 1

	# for i in xrange(05, 205, 10):
	# 	gap = 0
	# 	for t in range(trailNum):
	# 		start = int(round(time.time() * 1000))
	# 		examined, byte = algorithm.compute(i, 0)
	# 		end = int(round(time.time() * 1000))
	# 		gap += end - start
	# 	gap /= float(trailNum)
	# 	print str(i) + '\t' + str(examined) + '\t' + str(gap) + '\t' + str(byte)
		# print str(i) + '\t' + str(examined) + '\t' + str(byte)


def point_query_et(freq_data, selected_docs_list, global_scores):
	'''
		Estimate the cost of query, no real computation
	'''
	context_doc_groups = None
	algorithms = []
	for selected_docs in selected_docs_list:
		algorithm = OLAPORP_FAKE(freq_data, selected_docs, context_doc_groups, global_scores)
		algorithms.append(algorithm)
	import time
	trailNum = 1
	num_types = 3

	for type_code in range(num_types):
		print '====================== ' + str(type_code)
		for i in xrange(10, 205, 10):
			total_examimed = 0
			total_gap = 0
			total_byte = 0
			for algorithm in algorithms:
				gap = 0
				for t in range(trailNum):
					start = int(round(time.time() * 1000))
					examined, byte = algorithm.compute(i, type_code)
					end = int(round(time.time() * 1000))
					gap += end - start
				gap /= float(trailNum)
				total_examimed += examined
				total_byte += byte
				total_gap += gap
			avg_examined = total_examimed / float(len(algorithms))
			avg_gap = total_gap / float(len(algorithms))
			avg_byte = total_byte / float(len(algorithms))
			print str(i) + '\t' + str(avg_examined) + '\t' + str(avg_gap) + '\t' + str(avg_byte)
			# print str(i) + '\t' + str(examined) + '\t' + str(byte)




