import sys
# sys.path.insert(0, '../strategies')

from data_table import DataTable
from utils import get_all_legal_vals, get_all_ancestors, load_simple_measure
from utils import get_direct_parent
import itertools
import copy
import random
import math
import cPickle as pickle
from sets import Set

MAX_NUM = 100000000000000

class TextCube:
	
	def __init__(self, dt, ne_cells, sorted_cuboids, children_dict, children_dict_by_dim, hier_names, 
		raw_cost, merge_cost):
		self.dt = dt
		self.ne_cells = ne_cells
		self.sorted_cuboids = sorted_cuboids
		self.children_dict = children_dict
		self.children_dict_by_dim = children_dict_by_dim
		self.hier_names = hier_names
		self.lmda = 38.11

		self.raw_cost = raw_cost
		self.merge_cost = merge_cost

	def post_process(self):
		self.cost = copy.deepcopy(self.raw_cost)
		self.query_cost = copy.deepcopy(self.raw_cost)
		self.isMatered = copy.deepcopy(self.raw_cost)
		self.isVisited = copy.deepcopy(self.raw_cost)
		self.best_strategy = copy.deepcopy(self.raw_cost)
		for cell_str in self.isMatered:
			self.query_cost[cell_str] = 0
			self.isMatered[cell_str] = False
			self.isVisited[cell_str] = False
			self.best_strategy[cell_str] = None


	# def re_init(self):
	# 	self.cost = copy.deepcopy(self.raw_cost)
	# 	self.isMatered = copy.deepcopy(self.raw_cost)
	# 	self.isVisited = copy.deepcopy(self.raw_cost)
	# 	self.best_strategy = copy.deepcopy(self.raw_cost)

	# 	for cell_str in self.isMatered:
	# 		self.isMatered[cell_str] = False
	# 		self.isVisited[cell_str] = False
	# 		self.best_strategy[cell_str] = None


	def best_strategy_cell(self, cell_str):
		'''
			process the cell, find the best strategies and 
		'''
		if self.best_strategy[cell_str] != None:
			return self.best_strategy[cell_str], self.cost[cell_str]

		best_cost = self.raw_cost[cell_str]
		stra_str = 'raw'

		for hier_name in self.children_dict_by_dim[cell_str]:
			m_cost = self.merge_cost[cell_str][hier_name]
			for subcell in self.children_dict_by_dim[cell_str][hier_name]:
				m_cost += self.cost[subcell]
			if m_cost < best_cost:
				stra_str = hier_name

		self.best_strategy[cell_str] = stra_str
		self.cost[cell_str] = best_cost
		# self.isVisited[cell_str] = True
		
		return stra_str, best_cost

	def best_cost_query(self, cell_str):
		cell_stra, cell_cost = self.best_strategy_cell(cell_str)
		best_query_cost = cell_cost
		for sib in self.ne_cells[cell_str]['siblings']:
			cell_stra, cell_cost = self.best_strategy_cell(sib)
			best_query_cost += cell_cost

		self.query_cost[cell_str] = best_query_cost
		return best_query_cost


	def materilize_cell(self, cell_str):
		'''
		TODO: materialize the cell by the best strategy
		Currently only fakely materialize it
		'''
		self.isMatered[cell_str] = True
		self.cost[cell_str] = 1


	def full_mater(self):
		mat_cell_num = 0
		mat_record_num = 0
		for cuboid in self.sorted_cuboids:
			for cell_str in cuboid:
				mat_cell_num += 1
				mat_record_num += self.ne_cells[cell_str]['phraseN']
				self.isVisited[cell_str] = True

				self.query_cost[cell_str] = self.ne_cells[cell_str]['sibN'] + 1

		return mat_cell_num, mat_record_num

	def leaf_mater(self):
		mat_cell_num = 0
		mat_record_num = 0
		for cuboid in self.sorted_cuboids:
			isLeaf = True
			for cell_str in cuboid:
				if len(self.children_dict[cell_str]) > 0:
					isLeaf = False
					break
			if not isLeaf:
				for cell_str in cuboid:
					self.best_cost_query(cell_str)
				continue
			for cell_str in cuboid:
				mat_cell_num += 1
				mat_record_num += self.ne_cells[cell_str]['phraseN']
				self.isVisited[cell_str] = True
				self.query_cost[cell_str] = self.ne_cells[cell_str]['sibN'] + 1

		return mat_cell_num, mat_record_num


	def greedy_mater(self, T):
		cell_num = 0
		record_num = 0

		for cuboid in self.sorted_cuboids:
			cuboid = list(cuboid)
			random.shuffle(cuboid)
			for cell_str in cuboid:
				siblings = self.ne_cells[cell_str]['siblings']
				
				stra_str, best_cost = self.best_strategy_cell(cell_str)
				query_cost = best_cost

				for sib in siblings:
					stra_str, best_cost = self.best_strategy_cell(sib)
					query_cost += best_cost

				if query_cost > T:
					if not self.isMatered[cell_str]:
						self.materilize_cell(cell_str)
						cell_num += 1
						record_num += self.ne_cells[cell_str]['phraseN']
					for sib in siblings:
						if not self.isMatered[sib]:
							self.materilize_cell(sib)
							cell_num += 1
							record_num += self.ne_cells[sib]['phraseN']
				self.isVisited[cell_str] = True


			for cell_str in cuboid:
				x = self.best_cost_query(cell_str)
				if x > T:
					import ipdb
					ipdb.set_trace()


		return cell_num, record_num


	def utility_1(self, cell, T):
		sibN = self.ne_cells[cell]['sibN']
		cost_before_mater = self.cost[cell]
		return cost_before_mater

	def utility_2(self, cell, T):
		sibN = self.ne_cells[cell]['sibN']
		cost_before_mater = self.cost[cell]
		return (sibN + 1) * cost_before_mater

	def utility_3(self, cell, T):
		badN = len([sib for sib in self.ne_cells[cell]['siblings'] if self.query_cost[sib] >= T])
		if self.query_cost[cell] >= T:
			badN += 1
		cost_before_mater = self.cost[cell]
		return badN * cost_before_mater

	def utility_4(self, cell, T):
		sibN = self.ne_cells[cell]['sibN']
		return sibN + 1

	def utility_5(self, cell, T):
		badN = len([sib for sib in self.ne_cells[cell]['siblings'] if self.query_cost[sib] >= T])
		if self.query_cost[cell] >= T:
			badN += 1
		return badN



	def utility_mater(self, T, param):

		if param == 1:
			utility = self.utility_1
		if param == 2:
			utility = self.utility_2
		if param == 3:
			utility = self.utility_3
		if param == 4:
			utility = self.utility_4
		if param == 5:
			utility = self.utility_5

		cell_num = 0
		record_num = 0

		for cuboid in self.sorted_cuboids:
			cuboid = list(cuboid)
			random.shuffle(cuboid)
			# pre-process all cells and have their Q_cell and Q_query ready
			# random.shuffle(cuboid)
			for cell_str in cuboid:
				self.best_strategy_cell(cell_str)
			for cell_str in cuboid:
				query_cost = self.cost[cell_str]
				for sib in self.ne_cells[cell_str]['siblings']:
					query_cost += self.cost[sib]
				self.query_cost[cell_str] = query_cost

			
			# idx = 0
			# while True:
			# 	idx += 1
			# 	# print idx
			# 	sorted_cells_in_cuboid = sorted(cuboid, key=lambda x : self.query_cost[x], reverse=True)
			# 	cell_str = sorted_cells_in_cuboid[0]
			# 	if idx > 1000:
			# 		import ipdb
			# 		ipdb.set_trace()
			# 	if self.query_cost[cell_str] <= T:
			# 		break
			for cell_str in cuboid:
				q_cost = self.query_cost[cell_str]
				siblings = self.ne_cells[cell_str]['siblings']

				# import ipdb
				# ipdb.set_trace()

				# if cell_str == '41_1767':
				# 	import ipdb
				# 	ipdb.set_trace()
				# 	q_sib = [self.cost[sib] for sib in siblings]
				# 	ipdb.set_trace()
				# 	n_sib = [self.ne_cells[sib]['sibN'] for sib in siblings]
				# 	ipdb.set_trace()
				# 	max_n_sib = max(n_sib)
				# 	min_n_sib = min(n_sib)
				# 	ipdb.set_trace()
				# 	n_un_sib = []
				# 	for sib in siblings:
				# 		sNum = len([sibb for sibb in self.ne_cells[sib]['siblings'] if self.query_cost[sibb] >= T])
				# 		n_un_sib.append(sNum)
				# 	ipdb.set_trace()
				# 	print 'ssd'
					# n_no_sib = len([sibb for sibb in self.ne_cells[cell]['siblings'] if self.query_cost[sib] >= T])

				matered_cells = []
				utility_dict = {}
				if q_cost > T:
					if not self.isMatered[cell_str]:
						utility_dict[cell_str] = utility(cell_str, T)
					for sib in siblings:
						if not self.isMatered[sib]:
							utility_dict[sib] = utility(sib, T)
					sorted_uti = sorted(utility_dict.items(), key=lambda x : x[1], reverse=True)

					for u_cell_tuple in sorted_uti:
						u_cell = u_cell_tuple[0]
						matered_cells.append(u_cell)
						cost_before_mater = self.cost[u_cell]
						self.materilize_cell(u_cell)
						cell_num += 1
						record_num += self.ne_cells[u_cell]['phraseN']

						for u_sib in self.ne_cells[u_cell]['siblings']:
							self.query_cost[u_sib] = self.query_cost[u_sib] - (cost_before_mater - 1)
						self.query_cost[u_cell] -= (cost_before_mater - 1)

						q_cost -= (cost_before_mater - 1)
						if q_cost < T:
							break
				self.isVisited[cell_str] = True

			for cell_str in cuboid:
				self.best_cost_query(cell_str)

		return cell_num, record_num


	def materialize(self, mode, querySet, T=10000, param=1):
		'''
		-- mode --:
			FULL
			LEAF
			GREEDY
			UTI
		'''
		trial_num = 5
		total_cell_num = 0
		total_record_num = 0
		total_avg_cost = 0
		for i in range(trial_num):
			self.post_process()
			if mode == 'FULL':
				cell_num, record_num = self.full_mater()
			elif mode == 'LEAF':
				cell_num, record_num = self.leaf_mater()
			elif mode == 'GREEDY':
				cell_num, record_num = self.greedy_mater(T)
			elif mode == 'UTI':
				cell_num, record_num = self.utility_mater(T, param)

			avg_cost = self.exp_query_cost(mode, querySet)
			total_cell_num += cell_num
			total_record_num += record_num
			total_avg_cost += avg_cost
		

		avg_cost = total_avg_cost / float(trial_num)
		cell_num = total_cell_num / float(trial_num)
		record_num = total_record_num / float(trial_num)

		print mode + '\t' + str(T) + '\t' + str(cell_num) + '\t' + str(record_num) + '\t' + str(avg_cost)


	def exp_query_cost(self, mode, querySet, T=10000):
		total_cost = 0
		max_cost = 0

		# import ipdb
		# ipdb.set_trace()
		for query in querySet:
			total_cost += self.query_cost[query]
			if self.query_cost[query] > max_cost:
				max_cost = self.query_cost[query]

		avg_cost = total_cost / len(querySet)

		# print mode + '\t' + str(T) + '\t' + str(avg_cost)

		return max_cost



def count_ne_cells(dt, freq_data):
	
	def get_ne_siblings_cnt(cell):
		tokens = cell.split('_')
		index = 0
		count = 0
		sib_list = []
		for hier_name in hier_names:
			tokens_copy = list(tokens)
			hier_obj = hiers[hier_name]
			val_ori_id = int(tokens[index])
			# print hier_name
			# print val_ori_id
			# import ipdb
			# ipdb.set_trace()
			if val_ori_id == 0:
				sibling_ids = []
			else:
				sibling_ids = hier_obj.idd[hier_obj.ipd[val_ori_id][0]]
			for sid in sibling_ids:
				if sid == val_ori_id:
					pass
				tokens_copy[index] = sid
				tmp_str = '_'.join(str(x) for x in tokens_copy)
				if tmp_str in non_empty_cells:
					count += 1
					sib_list.append(tmp_str)
			index += 1
		return count, sib_list


	non_empty_cells = {}	# with siblings, format: {cell_str:(phrase_set, doc_num, sibling_num)}
	count = dt.records.shape[0]
	hiers = dt.hiers
	hier_names = hiers.keys()
	hier_values = {}
	total_uni_phrase = 0

	for hier_name, hier_obj in hiers.items():
		allnodes = get_all_legal_vals(hier_obj, 0)
		node_dict = {}	# the ancestor dict
		for node in allnodes:
			node_list = get_all_ancestors(hier_obj, node)
			node_dict[node] = node_list
		hier_values[hier_name] = node_dict


	children_dict = {}
	children_dict_by_dim = {}

	for i in range(count):
		if i % 1000 == 0:
			print i
		total_uni_phrase += len(freq_data[i])

		record = dt.records.loc[i]
		tmp_valid_lists = []	# all ancesters organized by dimensions
		is_valid_doc = True
		for hier_name in hier_names:
			hier_value = record[hier_name]
			if hier_value not in hier_values[hier_name]:
				print record
				is_valid_doc = False
				break
			else:
				tmp_valid_lists.append(hier_values[hier_name][hier_value])

		#print tmp_valid_lists
		if is_valid_doc:
			for element in itertools.product(*tmp_valid_lists):
				# print element
				tmp_str = '_'.join(str(x) for x in element)
				if tmp_str not in non_empty_cells:
					non_empty_cells[tmp_str] = {'phrases': Set(), 'docN': 0}
				non_empty_cells[tmp_str]['docN'] += 1
				phrases = freq_data[i].keys()
				non_empty_cells[tmp_str]['phrases'].update(phrases)

	

	for cell_str in non_empty_cells:
		tokens = cell_str.split('_')
		if cell_str not in children_dict:
			children_dict[cell_str] = Set()
			children_dict_by_dim[cell_str] = {}

		for idx, hier_name in enumerate(hier_names):

			hier_obj = hiers[hier_name]
			parent = get_direct_parent(hier_obj, int(tokens[idx]))
			if parent != None:
				tokens_copy = list(tokens)
				tokens_copy[idx] = parent
				tmp_str = '_'.join(str(x) for x in tokens_copy)
				if tmp_str not in children_dict:
					children_dict[tmp_str] = Set()
					children_dict_by_dim[tmp_str] = {}
				children_dict[tmp_str].add(cell_str)
				if hier_name not in children_dict_by_dim[tmp_str]:
					children_dict_by_dim[tmp_str][hier_name] = []
				children_dict_by_dim[tmp_str][hier_name].append(cell_str)
				# if tmp_str == '0_0':
					# print children_dict_by_dim[tmp_str]


	print 'computing average sibling number'
	# print non_empty_cells
	for cell in non_empty_cells:
		num_sib, sib_list = get_ne_siblings_cnt(cell)
		non_empty_cells[cell]['sibN'] = num_sib
		non_empty_cells[cell]['siblings'] = sib_list
		non_empty_cells[cell]['phraseN'] = len(non_empty_cells[cell]['phrases'])


	# how to generate the cuboid graph, actually it's just on the sibling space
	ne_cell_strs = Set(non_empty_cells.keys())

	cuboids = []

	while len(ne_cell_strs) > 0:
		cell_str = ne_cell_strs.pop()
		cuboid_set = Set()
		queue = Set([cell_str])
		while True:
			if len(queue) == 0:
				break
			cell_str = queue.pop()
			cuboid_set.add(cell_str)
			siblings = non_empty_cells[cell_str]['siblings']
			for sib in siblings:
				if sib not in cuboid_set:
					queue.add(sib)

		for cell_str in cuboid_set:
			if cell_str in ne_cell_strs:
				ne_cell_strs.remove(cell_str)

		cuboids.append((cuboid_set, Set()))
	

	for cuboid_pair in cuboids:
		cuboid = cuboid_pair[0]
		child_cells = cuboid_pair[1]
		for cell_str in cuboid:
			child_cells.update(children_dict[cell_str])

	sorted_cuboids = []

	while len(cuboids) > 0:
		cuboids = sorted(cuboids, key=lambda x: len(x[1]))
		if len(cuboids[0][1]) > 0:
			import ipdb
			ipdb.set_trace()			
			print 'error'
		target_cuboid = cuboids[0][0]
		sorted_cuboids.append(target_cuboid)
		cuboids.pop(0)
		for cuboid_pair in cuboids:
			child_cells = cuboid_pair[1]
			for cell_str in target_cuboid:
				if cell_str in child_cells:
					child_cells.remove(cell_str)

	

	#print non_empty_cells
	print 'Total cell number: %s' % len(non_empty_cells)
	print 'Average Unique Phrase Count in Each Doc %s' % (total_uni_phrase / float(count))

	# l = [len(non_empty_cells[x][0]) for x in non_empty_cells]
	l = [non_empty_cells[x]['phraseN'] for x in non_empty_cells]
	print 'Average Phrase Count: %.4f' % (reduce(lambda x, y: x + y, l) / float(len(l)))

	l = [non_empty_cells[x]['sibN'] for x in non_empty_cells]
	print 'Average Sibling Count: %.4f' % (reduce(lambda x, y: x + y, l) / float(len(l)))

	raw_cost = {}
	merge_cost = {}
	lmda = 38.11
	for cell_str in non_empty_cells:
		docN = non_empty_cells[cell_str]['docN']
		raw_cost[cell_str] = lmda * docN * math.log(docN, 2)
		merge_cost[cell_str] = {}
		for hier_name in children_dict_by_dim[cell_str]:
			m_cost = 0
			for subcell in children_dict_by_dim[cell_str][hier_name]:
				m_cost += non_empty_cells[subcell]['phraseN']
			merge_cost[cell_str][hier_name] = m_cost

	# import ipdb
	# ipdb.set_trace()

	textcube = TextCube(dt, non_empty_cells, sorted_cuboids, children_dict, 
		children_dict_by_dim, hier_names, raw_cost, merge_cost)

	pickle.dump(textcube, open('1d_cube.dump', 'wb'))


def create_cube():
	hier_meta_dict = {}
	hier_meta_dict['Location'] = '../data/raw/lochier.hier'
	# hier_meta_dict['Location'] = '../data/raw/new2_lochier.hier'
	# hier_meta_dict['Topic'] = '../data/raw/topichier.hier'

	# hier_meta_dict['Org'] = '../data/raw/orgtype.hier'
	# hier_meta_dict['Per'] = '../data/raw/pertype.hier'


	data_file = "../data/raw/data_table_4dim.csv"
	# data_file = "../data/raw/data_table.csv"
	# data_file = "../data/raw/new_data_table_no_ner.csv"
	pure_freq_file = "../data/processed/pure_freq_qualified_newid.txt"

	freq_data = load_simple_measure(pure_freq_file)
	# print freq_data[0]
	dt = DataTable(data_file, hier_meta_dict)

	count_ne_cells(dt, freq_data)


	# if len(sys.argv) < 3:
	# 	print "1. <usage> ncell [table file] [ file] [stopword file]"
	# 	print "2. <usage> avgsibling [pure_freq_file] [unfied file] [forward file]"
	# 	print "3. <usage> avgphrase [unified] [forward map] [cube file] [output file] [#docs] [target cell str]"
	# 	sys.exit(-1)


	# if sys.argv[1] == 'ncell':
	# 	pre_pre_process(sys.argv[2], sys.argv[3], sys.argv[4])

def load_cube():
	textcube = pickle.load(open('1d_cube.dump', 'rb'))
	textcube.post_process()

	print 'data loaded'

	# textcube.materialize('FULL')

	# Ts = [6400, 8800, 12800, 17500, 25600, 35000, 51200, 70000, 102400, 145000, 204800, 290000, 409600, 580000, 819200, 1150000, 1638400, 2250000, 3276800, 4400000, 6553600, 9100000, 13107200, 18000000]
	Ts = [580000]

	# generate sample queries
	queryN = 500
	querySet = Set()
	query_list = list(textcube.ne_cells.keys())
	random.shuffle(query_list)
	idx = 0
	for cell_str in query_list:
		if len(textcube.children_dict[cell_str]) > 0:
			querySet.add(cell_str)
			idx += 1
		if idx >= queryN:
			break

	textcube.materialize('FULL', querySet)
	# textcube.exp_query_cost('FULL', querySet)

	textcube.materialize('LEAF', querySet)
	# textcube.exp_query_cost('LEAF', querySet)



	# print '=============='

	for T in Ts:
		textcube.materialize('GREEDY', querySet, T)
		# textcube.materialize('UTI', T, 1)
		textcube.post_process()

	print '=============='
	for i in range(5):
		print 'UTILITY' + str(i)
		for T in Ts:
			# textcube.materialize('GREEDY', T)
			textcube.materialize('UTI', querySet, T, i + 1)
			# textcube.exp_query_cost('UTI', querySet, T=T)
			textcube.post_process()
		print '=============='

	# for T in Ts:
	# 	# textcube.materialize('GREEDY', T)
	# 	textcube.materialize('UTI', T, 2)
	# 	textcube.post_process()



	# import ipdb
	# ipdb.set_trace()


# create_cube()
load_cube()




