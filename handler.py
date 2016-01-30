from strategies.olaporp import point_query as pq_olaporp
from strategies.olaporp import point_query_et as pq_olaporp_et
from strategies.mcx_real import point_query as pq_mcx
from strategies.utils.utils import load_simple_measure as load_freq
from strategies.utils.utils import load_frequent_patterns as load_freq_patterns
from strategies.utils.utils import save_dict_list as save_phrase_features
from strategies.utils.utils import load_cube as load_cube
from strategies.utils.utils import load_context as load_context
from strategies.utils.utils import load_unified_list
from strategies.utils.utils import normalize_feature
from strategies.utils.utils import agg_phrase_cnt
from strategies.utils.utils import normalize
from query.data_table import DataTable
from operator import __add__
import traceback
import json
import sys
import copy
import math
import operator
import codecs
import random
import cPickle as pickle
import hashlib
import bencode


raw_file = 'data/raw/docs.txt'
qualified_docs_file = 'data/processed/qualified_docs.txt'
unified_list_file = 'data/processed/unified.csv'
freq_data_file = 'data/processed/pure_freq_qualified_newid.txt'
stopwords_file = 'data/raw/stopwords.txt'

num_of_docs = 41959

# create cell related
hier_meta_dict = {}
hier_meta_dict['Location'] = 'data/raw/lochier.hier'
#hier_meta_dict['Location'] = '../data/raw/new2_lochier.hier'
hier_meta_dict['Topic'] = 'data/raw/topichier.hier'
data_file = "data/raw/data_table.csv"




class Handler:

	def point_query(self, algorithm, selected_docs, context_groups, param=None):
		'''
		-- algorithm --
			OLAPORP: our algorithm
				-- param --
				ALL, POP, NOPOP, ......
			MCX
			SEG
			MCXSEG
		'''
		result_phrases = {}
		if algorithm == 'OLAPORP':
			result_phrases, olaporp_instance = pq_olaporp(self.freq_data, selected_docs, context_groups, self.unified_list, param)
		elif algorithm == 'MCX':
			result_phrases = pq_mcx(selected_docs, param)
		else:
			pass
		return result_phrases, olaporp_instance
	
	def create_cell_and_siblings(self, query, context='SIB'):
		'''
		-- context --
			SIB: siblings
			PAR: parents
			ALL: entire corpus
		'''

		attrs = ""
		selected_docs = []
		context_doc_groups = {}

		# generate cell docs
		for k, v in query.items():
			attrs += "{0}|{1};".format(k, v)
		try:
			selected_docs = self.dt.slice_and_return_doc_id(query)
			print "Attrs:{0};Doc#:{1}".format(attrs, len(selected_docs))
		except:
			print(traceback.format_exc())
			print "{0} failed to gen doc list".format(attrs)

		# Temp
		# context = 'ALL'

		# generate context
		if context == 'SIB':
			try:
				context_doc_groups = self.dt.slice_and_return_siblings(query)
				for context in context_doc_groups:
					context_doc_groups[context] = [doc for doc in context_doc_groups[context]]
				print "Attrs:{0};Siblings#:{1}".format(attrs, len(context_doc_groups))
			except:
				print(traceback.format_exc())
				print "{0} failed to gen doc list".format(attrs)


		elif context == 'PAR':
			try:
				context_doc_groups = self.dt.slice_and_return_parents(query)
				print "Attrs:{0};Parent#:{1}".format(attrs, len(context_doc_groups))
			except:
				print "{0} failed to gen doc list".format(attrs)
		elif context == 'ALL':
			context_doc_groups = None

		selected_docs = [doc for doc in selected_docs]

		return (attrs, selected_docs, context_doc_groups)


	# generate result by a point query
	def __init__(self):
		self.freq_data = load_freq(freq_data_file)
		self.unified_list = load_unified_list(unified_list_file)
		self.dt = DataTable(data_file, hier_meta_dict)



def create_dump():
	ratio = 0.9
	handler = Handler()

	query = {'Topic': 'Business'}
	cell_str, selected_docs, context_doc_groups = handler.create_cell_and_siblings(query)
	print 'Start computing phrases'

	us_docs = [doc for doc in handler.dt.slice_and_return_doc_id({'Topic': 'Business', 'Location': 'United States of America'})]
	abandon_docs = [us_docs[i] for i in random.sample(xrange(len(us_docs)), int(len(us_docs) * ratio))]

	print len(selected_docs)
	# abandon us docs
	for doc in abandon_docs:
		selected_docs.remove(doc)

	print len(selected_docs)

	result_phrases, olaporp_instance = handler.point_query('OLAPORP', selected_docs, context_doc_groups, 'ALL')
	inx = 0
	for phrase in result_phrases:
		if ' ' in phrase[0]:
			print phrase[0]
			inx += 1
		if inx >= 20:
			break
	print '========================================'
	pickle.dump(olaporp_instance, open('<Business>.dump', 'wb'))

	sys.exit()


def dcg(ranked_list):
	index = 1
	result_dcg = 0
	for (explain, rel_score) in ranked_list:
		result_dcg += rel_score / math.log(index + 1)
		index += 1
	return result_dcg


def evaluate(expls_origin, expls_new):
	'''
		The original expls must be the ranks and the new ones are just ranked by the measures
	'''
	phrases = expls_origin.keys()
	valid_cases = len(phrases)

	total_ndcg = 0
	for phrase in phrases:

		ori_rank = [rank for (method, rank) in expls_origin[phrase] if method == 'ORIGINAL'][0]

		ori_rank = 1/math.log(ori_rank + 2, 2)
		# The worst relevance is 0, not negative
		ori_ranked_list = [(explain, max(ori_rank - 1/math.log(value + 2, 2), 0)) for (explain, value) in expls_origin[phrase] if explain != 'ORIGINAL']
		ori_dict = dict(ori_ranked_list)

		ori_dcg = dcg(ori_ranked_list)
		
		# if there is no valid explanation, skip this case
		if ori_dcg <= 0:
			valid_cases -= 1
			continue

		new_ranked_list = [(explain, ori_dict[explain]) for (explain, value) in expls_new[phrase] if explain != 'ORIGINAL']
		new_dcg = dcg(new_ranked_list)

		total_ndcg += new_dcg / ori_dcg

	return total_ndcg / valid_cases


def handle_explanations(explanations):
	total_ndcg = 0

	import ipdb
	ipdb.set_trace()

	print evaluate(explanations['ranking'], explanations['ranking'])
	print evaluate(explanations['ranking'], explanations['delta'])
	print evaluate(explanations['ranking'], explanations['tf'])
	print evaluate(explanations['ranking'], explanations['subcmp'])
	print evaluate(explanations['ranking'], explanations['subcmpbi'])

	sys.exit()
	return ndcg



measures = {'ranking', 'delta', 'tf', 'subcmp', 'subcmpbi'}
cell_size_threshold = 40


if __name__ == "__main__":

	def load_dump():
		olaporp_instance = pickle.load(open('<Business>.dump', 'rb'))
		# target_phrase = 'domestic demand'
		return olaporp_instance

	def load_explanations():
		explanations = pickle.load(open('<Business>_exp.dump', 'rb'))
		return explanations

	# temp: for handle explanations
	# handle_explanations(load_explanations())

	# temp: create cell computation dump
	# create_dump()

	handler = Handler()

	



	# The case study queries
	grand_query = {'Topic': 'Business'}
	k = 100

	olaporp_instance = load_dump()
	all_docs = list(olaporp_instance.selected_docs)
	print 'ALL DOCS: %d' % len(all_docs)

	original_ranked_list = olaporp_instance.update_computing()

	# the examined phrases
	# single phrases
	# phrases = [[x[0]] for x in original_ranked_list[:k]]  # ['domestic demand', 'financial crisis', 'billion euros', 'economic growth', 'troubled banks']
	# multiple phrases
	number = 2
	test_case = 30
	phrases = []
	for i in range(test_case):
		phrases.append([original_ranked_list[i][0] for i in random.sample(xrange(k), number)])


	explanations = {}
	for measure in measures:
		explanations[measure] = {x : {} for x in phrases} 

	# add the default non-intervenation
	for phrase in phrases:
		phrase_key = '_'.join(phrase)

		for measure in measures:
			explanations[measure][phrase_key]['ORIGINAL'] = 0

		for ph in phrase:
			for i in range(len(original_ranked_list)):
				if original_ranked_list[i][0] == ph:
					index = i
					break
			explanations['delta'][phrase_key]['ORIGINAL'] += original_ranked_list[index][1]
			explanations['ranking'][phrase_key]['ORIGINAL'] += 1/math.log(index + 2, 2)
			explanations['tf'][phrase_key]['ORIGINAL'] += olaporp_instance.phrase_cnt[phrase]
			explanations['subcmp'][phrase_key]['ORIGINAL'] += 0
			explanations['subcmpbi'][phrase_key]['ORIGINAL'] += 0

	# Evaluation related

	hier = handler.dt.hiers['Location']

	# binary comp and full comp:
	all_countries = [hier.ind[x] for x in hier.idd[hier.ipd[hier.nid['China']][0]]]
	country_docs = {}
	original_docs = set(all_docs)
	for country in all_countries:
		query_dict = {'Topic': 'Business', 'Location': country}
		c_docs = [doc for doc in handler.dt.slice_and_return_doc_id(query_dict)]
		c_docs = [x for x in c_docs if x in original_docs]
		if len(c_docs) >= cell_size_threshold:
			country_docs[country] = c_docs


	for country in country_docs:
		query_dict = {'Topic': 'Business', 'Location': country}

		print 'running on :' + country
		selected_docs = list(country_docs[country])
		context_doc_groups = copy.deepcopy({key:value for key, value in country_docs.items() if key != country})
		result_phrases, sub_olap_instance = handler.point_query('OLAPORP', selected_docs, context_doc_groups, 'ALL')		
		ranked_dict = {x[0]:x[1] for x in result_phrases}

		for phs in phrases:
			phrase_key = '_'.join(phs)
			for measure in measures:
				explanations[measure][phrase_key][str(query_dict)] = 0
			
			for phrase in phs:
				if phrase not in ranked_dict:
					explanations['subcmp'][phrase_key][str(query_dict)] += 0
					continue
				index = 0
				for i in range(len(result_phrases)):
					if result_phrases[i][0] == phrase:
						index = i
						break
				# import ipdb
				# ipdb.set_trace()
				explanations['subcmp'][phrase_key][str(query_dict)] += -ranked_dict[phrase]

		# import ipdb
		# ipdb.set_trace()

		context_doc_groups = copy.deepcopy({'other_countries':reduce(__add__, [value for key, value in country_docs.items() if key != country])})

		result_phrases, sub_olap_instance = handler.point_query('OLAPORP', selected_docs, context_doc_groups, 'ALL')		
		ranked_dict = {x[0]:x[1] for x in result_phrases}

		for phs in phrases:
			phrase_key = '_'.join(phs)
			for phrase in phs:
				if phrase not in ranked_dict:
					explanations['subcmpbi'][phrase_key][str(query_dict)] += 0
					continue
				index = 0
				for i in range(len(result_phrases)):
					if result_phrases[i][0] == phrase:
						index = i
						break
				# import ipdb
				# ipdb.set_trace()
				explanations['subcmpbi'][phrase_key][str(query_dict)] += -ranked_dict[phrase]


	for country in [hier.ind[x] for x in hier.idd[hier.ipd[hier.nid['China']][0]]]:
		original_docs = list(all_docs)
		query = {'Topic': 'Business', 'Location': country}
		removed_ids = [doc for doc in handler.dt.slice_and_return_doc_id(query)]
		if len(removed_ids) < cell_size_threshold:
			continue

		print 'Examining Cell %s with %d' % (query, len(removed_ids))

		original_docs = [x for x in original_docs if x not in removed_ids]
		print len(original_docs)

		olaporp_instance.update_selected_docs(handler.freq_data, original_docs)
		ranked_list = olaporp_instance.update_computing()
		ranked_dict = {x[0]:x[1] for x in ranked_list}

		for phs in phrases:
			phrase_key = '_'.join(phs)
			for phrase in phs:
				index = 0
				for i in range(len(ranked_list)):
					if ranked_list[i][0] == phrase:
						index = i
						break
				explanations['delta'][phrase_key][str(query)] += ranked_dict[phrase]
				explanations['ranking'][phrase_key][str(query)] += 1/math.log(index + 2, 2)
				explanations['tf'][phrase_key][str(query)] += olaporp_instance.phrase_cnt[phrase]
	


	
	for phs in phrases:
		phrase_key = '_'.join(phs)
		for measure in measures:
			explanations[measure][phrase_key] = sorted(z)
		explanations['ranking'][phrase] = sorted(explanations['ranking'][phrase].items(), key=operator.itemgetter(1))
		explanations['delta'][phrase] = sorted(explanations['delta'][phrase].items(), key=operator.itemgetter(1))
		explanations['tf'][phrase] = sorted(explanations['tf'][phrase].items(), key=operator.itemgetter(1))
		explanations['subcmp'][phrase] = sorted(explanations['subcmp'][phrase].items(), key=operator.itemgetter(1), reverse=True)
		explanations['subcmpbi'][phrase] = sorted(explanations['subcmpbi'][phrase].items(), key=operator.itemgetter(1), reverse=True)
	
	pickle.dump(explanations, open('<Business>_exp.dump', 'wb'))



	# for phrase in phrases:
	# 	print "Top Explanations of \"%s\": Ranking" % phrase
	# 	print sorted(explanations_ranking[phrase].items(), key=operator.itemgetter(1), reverse=True)
	# 	print '\n'

	# 	print "Top Explanations of \"%s\": Delta" % phrase
	# 	print sorted(explanations_delta[phrase].items(), key=operator.itemgetter(1))
	# 	print '\n'

	# 	print "Top Explanations of \"%s\": TF" % phrase
	# 	print sorted(explanations_tf[phrase].items(), key=operator.itemgetter(1))
	
	# 	print '\n\n=========================================='


	sys.exit(1)	



	# output china, economy
	# query = {'Topic':'Business', 'Location':'China'}
	# cell_str, selected_docs, context_doc_groups = handler.create_cell_and_siblings(query)
	# print 'Start China, Economy'
	# result_phrases = handler.point_query('OLAPORP', selected_docs, context_doc_groups, 'ALL')
	# inx = 0
	# for phrase in result_phrases:
	# 	if ' ' in phrase[0]:
	# 		print phrase[0]
	# 		inx += 1
	# 	if inx >= k:
	# 		break

	# sys.exit(1)

	

	

	
	# sys.exit()

	



	# =============== find out the size of children of <Economy> ================
	# hier = handler.dt.hiers['Location']
	
	# pairs = []
	# for country in [hier.ind[x] for x in hier.idd[hier.ipd[hier.nid['China']][0]]]:
	# 	query = {'Topic': 'Business', 'Location': country}
	# 	count = handler.dt.doc_count(query)
	# 	if count > 0:
	# 		pairs.append((country, count))

	# pairs.sort(key=lambda x:x[1], reverse=True)
	# print pairs








