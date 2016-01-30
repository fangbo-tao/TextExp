import codecs
import os
import sys

def get_docs(data_cube_file):
  att_docs = {}
  with open(data_cube_file, "r") as f:
    for line in f:
      arr = line.strip().split(":")
      att = arr[0].replace(";", "_").replace("|", "_").replace(" ", "_")
      doc_str_list = arr[1].strip().split(",")
      doc_list = [int(d) for d in doc_str_list]
      att += "_" + str(len(doc_list))
      att_docs[att] = doc_list

  return att_docs


def write_to_file(original_file, att_docs, of_dir):
  for att, docs in att_docs.items():
    of = of_dir + "/" + att
    with codecs.open(original_file, "r", encoding="utf-8") as fin:
      with codecs.open(of, "w+", encoding="utf-8") as fo:
        index = -1
        for line in fin:
          index += 1
          if index not in docs:
            continue
          fo.write(line)


def train(shell_folder, if_dir, att_docs, train_data_src_file_name, train_result_file_name, of_dir):
  os.chdir(shell_folder)
  for att in att_docs:
    print "training", att
    src_file = if_dir + "/" + att
    os.system("cp " + src_file + " " + train_data_src_file_name)
    os.system("sh run2.sh")
    of = of_dir + "/" + att
    os.system("cp " + train_result_file_name + " " + of)


if __name__ == "__main__":
  if len(sys.argv) < 5:
    print "<usage> [data_cube_file] [shell_folder] [src folder] [result dir]"
    sys.exit()

  data_cube_file = sys.argv[1]
  shell_folder = sys.argv[2]
  if_dir = sys.argv[3]
  of_dir = sys.argv[4]

  att_docs = get_docs(data_cube_file)

  original_file = shell_folder + "/data/qualified.txt"
  #write_to_file(original_file, att_docs, if_dir)

  print "done with create src files"

  train_data_src_file_name = shell_folder + "/data/cell.txt"
  train_result_file_name = shell_folder + "results_case_study/unified.csv"
  train(shell_folder, if_dir, att_docs, train_data_src_file_name, train_result_file_name, of_dir)