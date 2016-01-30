from utils import agg_phrase_cnt
from utils import agg_phrase_df
from utils import normalize
import codecs
import math

class prettyfloat(float):
    def __repr__(self):
        return "%0.3f" % self

class ContextScore:

	def bm25(self, tf, dl, avgdl, k=1.2, b=0.5, smoothing=0.5):
		# tf = tf
		# print 'tf=' + str(tf)
		# print 'dl=' + str(dl)
		# print 'avgdl=' + str(avgdl)
		score = tf * (k + 1) / (tf + k * (1 - b + b * (dl / avgdl)))
		#score = max(score - 0.5, 0.07)
		return score

	def bm25_df(self, df, tf, dl, avgdl, idf_smooth=6, k=1.2, b=0.5, smoothing=0.5):
		score = tf * (k + 1) / (tf + k * (1 - b + b * (dl / avgdl)))
		score *= math.log(df + idf_smooth, 2)
		score /= math.log(1 + idf_smooth, 2)
		return score


	def bm25_df_paper(self, df, max_df, tf, dl, avgdl, k=1.2, b=0.5, multiplier=3):
		score = tf * (k + 1) / (tf + k * (1 - b + b * (dl / avgdl)))
		df_factor = math.log(1 + df, 2) / math.log(1 + max_df, 2)
		score *= df_factor
		score *= multiplier
		return score


	def bm25_df_4(self, df, tf, dl, avgdl, idf_smooth=6, k=1.2, b=0.5, smoothing=0.5):
		'''
		The new DF factor where its normalized from 0 to 1
		'''
		score = tf * (k + 1) / (tf + k * (1 - b + b * (dl / avgdl)))
		score *= math.log(df + idf_smooth, 2)
		score /= math.log(1 + idf_smooth, 2)
		return score


	def bm25_df_2(self, df, tf, dl, avgdl, k=1.2, b=0.5, smoothing=0.5):
		score = tf * (k + 1) / (tf + k * (1 - b + b * (dl / avgdl)))
		idf_factor = 1 / math.log(1 + tf / float(df) , 2)
		score *= idf_factor

		return score

	def bm25_df_3(self, df, tf, dc, dl, avgdl, k=1.2, b=0.5, smoothing=0.5):
		score = tf * (k + 1) / (tf + k * (1 - b + b * (dl / avgdl)))
		idf_factor = 1 / math.log(1 + dc / float(df))
		# idf_factor = 1 / math.log(1 + tf / float(df) , 2)
		score *= idf_factor

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



	def softmax(self, score_list, cell_num, default_value=10):
		per_cell_default = default_value / float(cell_num)
		if len(score_list) > cell_num:
			print 'Error happend for list ' + str(score_list)
		exp_sum = (cell_num - len(score_list)) * per_cell_default
		for score in score_list:
			exp_sum += math.exp(score)

		exp_list = []
		for score in score_list:
			normal_value = math.exp(score) / exp_sum
			exp_list.append(normal_value)

		return exp_list


	def __init__(self, freq_data, selected_doc=None, context_doc_groups=None, total_cnt=None, global_scores=None):
		self.phrase_cnt = agg_phrase_cnt(freq_data, selected_doc)
		self.phrase_df = agg_phrase_df(freq_data, selected_doc)
		self.phrase_cnt_context = {}
		self.phrase_df_context = {}
		self.max_df = max(self.phrase_df.values())
		self.max_df_context = {}
		self.dc_context = {}
		self.self_dc = len(selected_doc)
		self.sum_cnt = sum(self.phrase_cnt.values())
		self.sum_cnt_context = {}
		self.global_scores = global_scores
		for group, docs in context_doc_groups.items():
			if len(docs) == 1 and docs[0] == '-1':
				self.phrase_cnt_context[group] = total_cnt
			else:
				self.phrase_cnt_context[group] = agg_phrase_cnt(freq_data, docs)
				self.phrase_df_context[group] = agg_phrase_df(freq_data, docs)
				self.max_df_context[group] = max(self.phrase_df_context[group].values())
				self.dc_context[group] = len(docs)
			self.sum_cnt_context[group] = sum(self.phrase_cnt_context[group].values())


	def compute_context_score(self, smooth=0.5):
		phrase_context_score = {}
		multiplier = 3.5

		log_file = open('_context_log', 'w+')
		
		log_strs = {}
		log_scores = {}
		
		sum_self = self.sum_cnt
		num_context_cells = len(self.sum_cnt_context) + 1
		total_sum = sum(self.sum_cnt_context.values()) + sum_self
		avgdl = total_sum / float(num_context_cells)
		print 'avgdl=' + str(avgdl)
		# method 1
		for phrase in self.phrase_cnt:
			lower_phrase = phrase.lower()
			score = 1
			self_cnt = self.phrase_cnt[phrase]
			
			group = [(self_cnt, sum_self)]
			for phrase_group, phrase_values in self.phrase_cnt_context.items():
				sum_context = self.sum_cnt_context[phrase_group]
				context_cnt = phrase_values.get(phrase, 0)
				if (context_cnt > 0):
					group.append((context_cnt, sum_context))
				
			score_list = []
			for record in group:
				score_list.append(self.bm25(record[0], record[1], avgdl))
			score = self.softmax(score_list, num_context_cells)[0] * multiplier
			
			score_list = map(prettyfloat, score_list)
			log_str = lower_phrase.encode('utf-8') + ':' + str(prettyfloat(score)) + '\t' +  str(group) +  '\t' + str(score_list) + '\n'
			log_strs[lower_phrase] = log_str
			log_scores[lower_phrase] = score


			# if (lower_phrase == 'rare earth'):
			# 	print 'target phrase'
			# 	print group
			# 	print score_list
			# 	print score / multiplier

			phrase_context_score[phrase] = score
		
		for phrase in sorted(log_scores, key=log_scores.get, reverse=True):
			log_file.write(log_strs[phrase])

		log_file.close()
		print 'context feature done'

		# experiment
		# self.compute_context_score_idf()
		self.compute_context_score_paper()

		return phrase_context_score


	def compute_context_score_paper(self):
		phrase_context_score = {}
		multiplier = 1

		log_file = open('_context_log_paper_1', 'w+')
		log_file_2 = open('_context_log_paper_2', 'w+')
		log_file_3 = open('_context_log_paper_3', 'w+')
		log_file_4 = open('_context_log_paper_4_classification', 'w+')
		log_strs = {}
		log_strs_2 = {}
		log_strs_3 = {}
		log_scores = {}
		log_scores_2 = {}
		log_scores_3 = {}
		
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
			for phrase_group, phrase_values in self.phrase_cnt_context.items():
				context_df = self.phrase_df_context[phrase_group].get(phrase, 0)
				sum_context = self.sum_cnt_context[phrase_group]
				context_cnt = phrase_values.get(phrase, 0)
				maxdf_context = self.max_df_context[phrase_group]

				if (context_cnt > 0):
					group.append((context_df, maxdf_context, context_cnt, sum_context))
				
			score_list = []
			for record in group:
				score_list.append(self.bm25_df_paper(record[0], record[1], record[2], record[3], avgdl))
			score = self.softmax_paper(score_list)[0]
			# score *= math.log(1 + self_cnt, 2)
			
			score_list = map(prettyfloat, score_list)
			log_str = lower_phrase.encode('utf-8') + ':' + str(prettyfloat(score)) + '\t' + str(score_list) + '\n'
			# log_str = lower_phrase.encode('utf-8') + ':' + str(prettyfloat(score)) + '\t' +  str(group) +  '\t' + str(score_list) + '\n'
			log_strs[lower_phrase] = log_str
			log_scores[lower_phrase] = score

			distinct = score
			popularity = math.log(1 + self_df, 2)

			score_2 = popularity * distinct
			log_str_2 = lower_phrase.encode('utf-8') + ':' + str(prettyfloat(score_2)) + '\t' + str(popularity) + '\t' + str(distinct)+ '\n'
			log_strs_2[lower_phrase] = log_str_2
			log_scores_2[lower_phrase] = score_2

			try:
				integrity = float(self.global_scores[nor_phrase])
			except:
				print nor_phrase
				continue

			score_3 = popularity * distinct * integrity
			log_str_3 = lower_phrase.encode('utf-8') + ':' + str(prettyfloat(score_3)) + '\t' + str(popularity) + '\t' + str(distinct)+ '\t' + str(integrity) + '\n'
			log_strs_3[lower_phrase] = log_str_3
			log_scores_3[lower_phrase] = score_3


			# if (lower_phrase == 'rare earth'):
			# 	print 'target phrase'
			# 	print group
			# 	print score_list
			# 	print score / multiplier

			phrase_context_score[phrase] = score
		
		for phrase in sorted(log_scores, key=log_scores.get, reverse=True):
			log_file.write(log_strs[phrase])

		for phrase in sorted(log_scores_2, key=log_scores_2.get, reverse=True):
			log_file_2.write(log_strs_2[phrase])

		for phrase in sorted(log_scores_3, key=log_scores_3.get, reverse=True):
			log_file_3.write(log_strs_3[phrase])

		for phrase in sorted(log_scores_3, key=log_scores_3.get, reverse=True)[:500]:
			nor_phrase = normalize(phrase)
			log_file_4.write(nor_phrase + ',')


		log_file.close()
		log_file_2.close()
		log_file_3.close()
		log_file_4.close()
		print 'context feature done'
		return phrase_context_score


	def compute_context_score_idf(self, smooth=0.5):
		phrase_context_score = {}
		multiplier = 1

		log_file = open('_context_log_df_with_tf', 'w+')
		log_strs = {}
		log_scores = {}
		
		sum_self = self.sum_cnt
		num_context_cells = len(self.sum_cnt_context) + 1
		total_sum = sum(self.sum_cnt_context.values()) + sum_self
		avgdl = total_sum / float(num_context_cells)

		# method 1
		for phrase in self.phrase_cnt:
			lower_phrase = phrase.lower()
			score = 1
			self_cnt = self.phrase_cnt[phrase]
			self_df = self.phrase_df[phrase]
			
			group = [(self_df, self_cnt, sum_self)]
			for phrase_group, phrase_values in self.phrase_cnt_context.items():
				context_df = self.phrase_df_context[phrase_group].get(phrase, 0)
				sum_context = self.sum_cnt_context[phrase_group]
				context_cnt = phrase_values.get(phrase, 0)

				if (context_cnt > 0):
					group.append((context_df, context_cnt, sum_context))
				
			score_list = []
			for record in group:
				score_list.append(self.bm25_df(record[0], record[1], record[2], avgdl))
			score = self.softmax(score_list, num_context_cells)[0]
			score *= math.log(1 + self_cnt, 2)
			
			score_list = map(prettyfloat, score_list)
			log_str = lower_phrase.encode('utf-8') + ':' + str(prettyfloat(score)) + '\t' +  str(group) +  '\t' + str(score_list) + '\n'
			log_strs[lower_phrase] = log_str
			log_scores[lower_phrase] = score


			# if (lower_phrase == 'rare earth'):
			# 	print 'target phrase'
			# 	print group
			# 	print score_list
			# 	print score / multiplier

			phrase_context_score[phrase] = score
		
		for phrase in sorted(log_scores, key=log_scores.get, reverse=True):
			log_file.write(log_strs[phrase])

		log_file.close()
		print 'context feature done'
		return phrase_context_score


	# def compute_context_score_idf_2(self, smooth=0.5):
	# 	phrase_context_score = {}
	# 	multiplier = 3.5

	# 	log_file = open('_context_log_idf_2', 'w+')
	# 	log_strs = {}
	# 	log_scores = {}
		
	# 	sum_self = self.sum_cnt
	# 	num_context_cells = len(self.sum_cnt_context) + 1
	# 	total_sum = sum(self.sum_cnt_context.values()) + sum_self
	# 	avgdl = total_sum / float(num_context_cells)

	# 	# method 1
	# 	for phrase in self.phrase_cnt:
	# 		lower_phrase = phrase.lower()
	# 		score = 1
	# 		self_cnt = self.phrase_cnt[phrase]
	# 		self_df = self.phrase_df[phrase]
			
	# 		group = [(self_df, self_cnt, sum_self)]
	# 		for phrase_group, phrase_values in self.phrase_cnt_context.items():
	# 			context_df = self.phrase_df_context[phrase_group].get(phrase, 0)
	# 			sum_context = self.sum_cnt_context[phrase_group]
	# 			context_cnt = phrase_values.get(phrase, 0)

	# 			if (context_cnt > 0):
	# 				group.append((context_df, context_cnt, sum_context))
				
	# 		score_list = []
	# 		for record in group:
	# 			score_list.append(self.bm25_df_2(record[0], record[1], record[2], avgdl))
	# 		score = self.softmax(score_list, num_context_cells)[0] * multiplier
			
	# 		score_list = map(prettyfloat, score_list)
	# 		log_str = lower_phrase.encode('utf-8') + ':' + str(prettyfloat(score)) + '\t' +  str(group) +  '\t' + str(score_list) + '\n'
	# 		log_strs[lower_phrase] = log_str
	# 		log_scores[lower_phrase] = score


	# 		# if (lower_phrase == 'rare earth'):
	# 		# 	print 'target phrase'
	# 		# 	print group
	# 		# 	print score_list
	# 		# 	print score / multiplier

	# 		phrase_context_score[phrase] = score
		
	# 	for phrase in sorted(log_scores, key=log_scores.get, reverse=True):
	# 		log_file.write(log_strs[phrase])

	# 	log_file.close()
	# 	print 'context feature done'
	# 	return phrase_context_score



	# # def compute_context_score_idf_3(self, smooth=0.5):
	# # 	phrase_context_score = {}
	# # 	multiplier = 3.5

	# # 	log_file = open('_context_log_idf_3', 'w+')
	# # 	log_strs = {}
	# # 	log_scores = {}
		
	# # 	sum_self = self.sum_cnt
	# # 	self_dc = self.self_dc
	# # 	num_context_cells = len(self.sum_cnt_context) + 1
	# # 	total_sum = sum(self.sum_cnt_context.values()) + sum_self
	# # 	avgdl = total_sum / float(num_context_cells)

	# # 	# method 1
	# # 	for phrase in self.phrase_cnt:
	# # 		lower_phrase = phrase.lower()
	# # 		score = 1
	# # 		self_cnt = self.phrase_cnt[phrase]
	# # 		self_df = self.phrase_df[phrase]
			
	# # 		group = [(self_df, self_cnt, self_dc, sum_self)]
	# # 		for phrase_group, phrase_values in self.phrase_cnt_context.items():
	# # 			context_df = self.phrase_df_context[phrase_group].get(phrase, 0)
	# # 			sum_context = self.sum_cnt_context[phrase_group]
	# # 			context_cnt = phrase_values.get(phrase, 0)
	# # 			this_dc_context = self.dc_context[phrase_group]

	# # 			if (context_cnt > 0):
	# # 				group.append((context_df, context_cnt, this_dc_context, sum_context))
				
	# # 		score_list = []
	# # 		for record in group:
	# # 			score_list.append(self.bm25_df_3(record[0], record[1], record[2], record[3], avgdl))
	# # 		score = self.softmax(score_list, num_context_cells)[0] * multiplier
			
	# # 		score_list = map(prettyfloat, score_list)
	# # 		log_str = lower_phrase.encode('utf-8') + ':' + str(prettyfloat(score)) + '\t' +  str(group) +  '\t' + str(score_list) + '\n'
	# # 		log_strs[lower_phrase] = log_str
	# # 		log_scores[lower_phrase] = score


	# # 		# if (lower_phrase == 'rare earth'):
	# # 		# 	print 'target phrase'
	# # 		# 	print group
	# # 		# 	print score_list
	# # 		# 	print score / multiplier

	# # 		phrase_context_score[phrase] = score
		
	# # 	for phrase in sorted(log_scores, key=log_scores.get, reverse=True):
	# # 		log_file.write(log_strs[phrase])

	# # 	log_file.close()
	# # 	print 'context feature done'
	# # 	return phrase_context_score