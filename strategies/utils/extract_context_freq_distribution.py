from utils import agg_phrase_cnt
import codecs
import operator
import math

class ContextFreqDist:

	def __init__(self, freq_data, selected_doc=None, context_doc_groups=None, total_cnt=None):
		self.phrase_cnt = agg_phrase_cnt(freq_data, selected_doc)
		self.phrase_cnt_context = {}
		self.sum_cnt = sum(self.phrase_cnt.values())
		self.sum_cnt_context = {}
		print self.sum_cnt
		for group, docs in context_doc_groups.items():
			if len(docs) == 1 and docs[0] == '-1':
				self.phrase_cnt_context[group] = total_cnt
			else:
				self.phrase_cnt_context[group] = agg_phrase_cnt(freq_data, docs)
			self.sum_cnt_context[group] = sum(self.phrase_cnt_context[group].values())
			print self.sum_cnt_context[group]


	def compute_context_freq_dist(self, formula=0, smooth=0, factor=10000):
		phrase_context_freq = {}
		
		sum_self = self.sum_cnt
		# method 1
		for phrase in self.phrase_cnt:
			dist_str = ''
			score = 1
			self_cnt = self.phrase_cnt[phrase] + smooth
			self_portion = factor * self_cnt / float(sum_self)
			dist_str += 'self:%.3f,%d,%d' % (self_portion, self_cnt, sum_self)
			portion_dict = {}
			cnt_dict = {}
			if formula == 0:
				for phrase_group, phrase_values in self.phrase_cnt_context.items():
					sum_context = self.sum_cnt_context[phrase_group]

					context_cnt = phrase_values.get(phrase, 0) + smooth					
					portion_context = factor * context_cnt / float(sum_context)
					portion_dict[phrase_group] = portion_context
					cnt_dict[phrase_group] = int(context_cnt)

				sorted_portions = sorted(portion_dict, key=portion_dict.get, reverse=True)
				for group in sorted_portions:
					dist_str += '|%s:%.3f,%d,%d' % (group, portion_dict[group], cnt_dict[group], self.sum_cnt_context[group])

			#temp_str += ',' + str(score)
			#print temp_str
			phrase_context_freq[phrase] = dist_str
			
		return phrase_context_freq

