from utils.utils import load_cube as load_cube
import sys

def concat_docs(cell_file, doc_file, output_file, cell_str):
	cells = load_cube(cell_file)

	with open(doc_file, 'r') as doc_file:
		docs = doc_file.readlines()



	for att in cells:
		if att != cell_str:
			continue
		selected_docs = cells[att]

		with open(output_file, 'w+') as g:
			for doc_id in selected_docs:
				g.write(docs[doc_id])


if __name__ == "__main__":
	if len(sys.argv) < 4:
		print "<usage> [cell file] [doc raw file] [output file] [cell str]"
	concat_docs(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
