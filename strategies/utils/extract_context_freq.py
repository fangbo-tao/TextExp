from utils import agg_phrase_cnt
import codecs
import math

class ContextFreq:

	def __init__(self, freq_data, selected_doc=None, context_doc_groups=None, total_cnt=None):
		self.phrase_cnt = agg_phrase_cnt(freq_data, selected_doc)
		self.phrase_cnt_context = {}
		self.sum_cnt = sum(self.phrase_cnt.values())
		self.sum_cnt_context = {}
		for group, docs in context_doc_groups.items():
			if len(docs) == 1:
				self.phrase_cnt_context[group] = total_cnt
			else:
				self.phrase_cnt_context[group] = agg_phrase_cnt(freq_data, docs)
			self.sum_cnt_context[group] = sum(self.phrase_cnt_context[group].values())


	def compute_context_freq(self, formula=0, smooth=0.5):
		phrase_context_freq = {}
		
		sum_self = self.sum_cnt

		log_file = open('_context_log_parents', 'w+')
		score_strs = {}
		# method 1
		for phrase in self.phrase_cnt:
			temp_str = phrase.lower().encode('utf-8') 
			score = 1
			self_cnt = self.phrase_cnt[phrase] + smooth
			temp_str += ',' + str(self_cnt)
			if formula == 0:
				for phrase_group, phrase_values in self.phrase_cnt_context.items():
					sum_context = self.sum_cnt_context[phrase_group]
					context_cnt = phrase_values.get(phrase, 0) + smooth
					portion_self = self_cnt / float(sum_self)
					portion_context = context_cnt / float(sum_context)
					temp_str += ',' + str(context_cnt)
					score *= (portion_self / portion_context)
				temp_str += ',' + str(score)
				score = math.log(score + 1)
				score *= math.log(self_cnt + 1)
			temp_str += ',' + str(score) + '\n'

			score_strs[phrase] = temp_str
			phrase_context_freq[phrase] = score

		for phrase in sorted(phrase_context_freq, key=phrase_context_freq.get, reverse=True):
			log_file.write(score_strs[phrase])

		log_file.close()

		return phrase_context_freq

