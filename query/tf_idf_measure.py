from utils import load_simple_measure
import codecs
import math

class TFIDFMeasure:
  def __init__(self, measure_file):
    self.measure_data = load_simple_measure(measure_file)

  def compute_idf(self):
    phrase_doc_count = {}
    for doc_index in self.measure_data:
      for phrase in self.measure_data[doc_index]:
        if phrase not in phrase_doc_count:
          phrase_doc_count[phrase] = 0
        phrase_doc_count[phrase] += 1

    phrase_idf = {}
    doc_num = len(self.measure_data)
    for phrase, cnt in phrase_doc_count.items():
      phrase_idf[phrase] = math.log(1 + float(doc_num) / (cnt + 1), 2)

    return phrase_idf


  def agg_count(self, doc_list):
    phrase_measure_dict = {}
    for doc_index in doc_list:
      if doc_index not in self.measure_data:
        continue
      for phrase, measure in self.measure_data[doc_index].items():
        if phrase not in phrase_measure_dict:
          phrase_measure_dict[phrase] = 0
        phrase_measure_dict[phrase] += measure

    return phrase_measure_dict

  def compute_tf(self, doc_list):
    phrase_cnt = self.agg_count(doc_list)
    max_cnt = max(phrase_cnt.values())

    phrase_tf = {}
    for phrase, cnt in phrase_cnt.items():
      #phrase_tf[phrase] = 0.5 + 0.5 * cnt / max_cnt  #version 1
      #phrase_tf[phrase] = 1 + math.log(cnt)  #version 2
      #phrase_tf[phrase] = 0.1 + 0.9 * cnt / max_cnt  #version 3
      phrase_tf[phrase] = 0.3 + 0.7 * cnt / max_cnt

    return phrase_tf

  def agg(self, doc_list):
    phrase_idf = self.compute_idf()
    phrase_tf = self.compute_tf(doc_list)

    phrase_score = {}
    for phrase in phrase_tf:
      phrase_score[phrase] = phrase_tf[phrase] * phrase_idf[phrase]

    return phrase_score


def main(m_file, d_file, o_file):
  measure = TFIDFMeasure(m_file)
  with open(d_file, "r") as df:
    with codecs.open(o_file, "w+", encoding='utf-8') as of:
      for line in df:
        arr = line.strip().split(':')
        att = arr[0]
        doc_list_str = arr[1].strip().split(",")
        doc_list = [int(d) for d in doc_list_str]

        res = measure.agg(doc_list)

        res_sorted = [(m, p) for p, m in res.items()]
        res_sorted.sort(reverse=True)

        pms = [u"{0}|{1}".format(p, m) for m, p in res_sorted]
        wline = u"{0}({1}):{2}\n".format(att, len(doc_list), ",".join(pms))

        of.write(wline)


if __name__ == "__main__":
  main('/home/qiwang12/10_05/invertedindex/unigram/pure_freq_qualified_newid.txt', './data/cubes.txt', './res/unigram/query_tf_idf_3.txt')
