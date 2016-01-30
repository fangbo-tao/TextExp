import codecs
import sys

def load_phrase_score(file_name):
  phrase_score = {}
  with codecs.open(file_name, "r", encoding="utf-8") as f:
    for line in f:
      arr = line.strip().split(",")
      phrase = arr[0]
      score = float(arr[1])
      phrase_score[phrase] = score
  return phrase_score

def parse_docs(doc_file, selected_docs):
  phrase_dict = {}
  with codecs.open(doc_file, "r", encoding="utf-8") as f:
    index = -1
    for doc in f:
      index += 1
      if index not in selected_docs:
        continue
      is_in_phrase = False
      phrase = ""
      for ch in doc:
        if ch == "[":
          phrase = ""
          is_in_phrase = True
        elif ch == "]":
          phrase = phrase.strip()
          if phrase != "":
            arr = phrase.split()
            phrase = "_".join(arr)
            phrase_dict[phrase] = 1
            is_in_phrase = False
            phrase = ""
        else:
          if is_in_phrase == True:
            if ch.isalpha():
              phrase += ch.lower()
            elif ch == "'":
              phrase += ch
            else:
              phrase += " "

  return phrase_dict

def get_docs(data_cube_file):
  att_docs = {}
  with open(data_cube_file, "r") as f:
    for line in f:
      arr = line.strip().split(":")
      att = arr[0]
      doc_str_list = arr[1].strip().split(",")
      doc_list = [int(d) for d in doc_str_list]
      att_docs[att] = doc_list

  return att_docs

def rank_phrase(phrase_dict, phrase_score):
  score_phrase = []
  for phrase in phrase_dict:
    score = phrase_score.get(phrase, -1)
    score_phrase.append((score, phrase))
  score_phrase.sort(reverse=True)
  return score_phrase

def write_ranking(score_phrase, of):
  with codecs.open(of, "w+", encoding="utf-8") as f:
    for score, phrase in score_phrase:
      f.write(u"{0}\t{1}\n".format(phrase, score))

def extract_global_score(ph_score_file, data_cube_file, parsed_file, out_dir):
  phrase_score = load_phrase_score(ph_score_file)
  att_docs = get_docs(data_cube_file)
  print "######docs: ", att_docs
  for att, docs in att_docs.items():
    phrase_dict = parse_docs(parsed_file, docs)
    print "##########phrase len", len(phrase_dict)
    score_phrase = rank_phrase(phrase_dict, phrase_score)
    att = att.replace(";", "_").replace("|", "_") + "_" + str(len(docs))
    of = out_dir + "/" + att
    print of
    write_ranking(score_phrase, of)

if __name__ == "__main__":
  if len(sys.argv) < 5:
    print "<usage> [phrase score file] [data cube file] [parsed file] [out directory]"
    sys.exit(-1)

  extract_global_score(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
