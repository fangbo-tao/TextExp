from utils import load_simple_measure
import codecs

class Measure:
  def __init__(self, measure_file):
    self.measure_data = load_simple_measure(measure_file)

  def agg(self, doc_list):
    phrase_measure_dict = {}
    for doc_index in doc_list:
      if doc_index not in self.measure_data:
        continue
      for phrase, measure in self.measure_data[doc_index].items():
        if phrase not in phrase_measure_dict:
          phrase_measure_dict[phrase] = 0
        phrase_measure_dict[phrase] += measure

    return phrase_measure_dict


def main(m_file, d_file, o_file):
  measure = Measure(m_file)
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
  main('/home/qiwang12/10_05/invertedindex/unigram/pure_freq_qualified_newid.txt', './data/cubes.txt', './res/unigram/query_res_pure_freq.txt')
  main('/home/qiwang12/10_05/invertedindex/unigram/lc_gb_qualified_newid.txt', './data/cubes.txt', './res/unigram/query_res_lc_gb.txt')
