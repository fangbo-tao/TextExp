import sys

def load_qualified_doc_id(q_file):
  qualified_docs = {}
  with open(q_file, 'r') as f:
    for line in f:
      doc_id = int(line.strip())
      qualified_docs[doc_id] = 1

  return qualified_docs

def select(in_file, qualified_doc_file, out_file):
  qualified_docs = load_qualified_doc_id(qualified_doc_file)
  with open(in_file, 'r') as in_f:
    with open(out_file, 'w+') as o_f:
      index = -1
      for line in in_f:
        index += 1
        if index in qualified_docs:
          out_file.write(line)

if __name__ == '__main__':
  if len(sys.argv) < 4:
    print "<usage> [source file] [qualified doc file] [out file]"
  select(sys.argv[1], sys.argv[2], sys.argv[3])