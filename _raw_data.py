from strategies.utils.utils import load_raw_text
import codecs
import ast
from random import shuffle
""" Generate raw text data after normalize the text, used for mcx baseline
"""


def generate_raw_file():
	g = open('docs.txt', 'w+')
	with open('data/raw/raw_docs.txt', 'r') as f:
		for line in f:
			new_line = line.replace('[', ' ')
			new_line = new_line.replace(']', ' ')
			new_line = new_line.replace('  ', ' ')
			g.write(new_line)

	g.close()


def generate_gist():
	raw_file = 'data/raw/docs.txt'
	raw_text = load_raw_text(raw_file)

	cells = {}
	cell_file = 'data/exp/pairs_MCX_BASIC.txt'
	f = open(cell_file, 'r')

	for line in f:
		cs = line.strip('\n').split('#')
		for c in cs:
			tokens = c.strip('\n').split(':')
			docs = tokens[1].split(',')
			cells[tokens[0]] = docs

	base_dir = 'data/exp/gist_'
	for cell in cells:
		g = codecs.open(base_dir + cell, "w+", encoding="utf-8")
		gist_list = []
		for doc in cells[cell]:
			gist_list.append(raw_text[int(doc)][:200])

		shuffle(gist_list)
		content = '\n'.join(gist_list)
		g.write(content)
		g.close()

def rank_phrase_by_tf():
	raw_file = open('strategies/_context_log_fake', 'r')

	lists = {}

	idx = 0
	for line in raw_file:
		phrase_list = ast.literal_eval(line.strip('\n'))
		lists[idx] = (phrase_list, phrase_list[0][2])
		idx += 1

	sorted_p = sorted(lists.items(), key=lambda x:x[1][1], reverse=True)

	# import ipdb
	# ipdb.set_trace()
	g = open('strategies/_context_log_fake_dist', 'w+')
	# print 'hahah'
	for p in sorted_p:
		# import ipdb
		# ipdb.set_trace()
		phrase_list = p[1][0][1:]
		line = str(phrase_list) + '\n'
		g.write(line)

	g.close()


def test_disk_speed():
	raw_file = open('strategies/_context_log_fake', 'rb')
	import random
	import time
	MAXNUM = 100000000
	random_list = []
	for i in range(10000):
		random_list.append(random.randint(0, MAXNUM))

	timeBegin = time.time() * 1000
	for i in range(10000):
		# raw_file.seek(random_list[i], 0)
		raw_file.read(1)
			
	timeEnd = time.time() * 1000

	print timeEnd - timeBegin


# rank_phrase_by_tf()	
test_disk_speed()


