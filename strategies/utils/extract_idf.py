import math

class IDFMeasure:
  def __init__(self, freq_data, selected_doc = None):
    self.freq_data = freq_data
    self.selected_doc = selected_doc

  def compute_idf(self):
    phrase_doc_count = {}
    for doc_index in self.freq_data:
      if self.selected_doc is not None and doc_index not in self.selected_doc:
        continue
      for phrase in self.freq_data[doc_index]:
        if phrase not in phrase_doc_count:
          phrase_doc_count[phrase] = 0
        phrase_doc_count[phrase] += 1

    phrase_idf = {}
    doc_num = len(self.freq_data)
    for phrase, cnt in phrase_doc_count.items():
      phrase_idf[phrase] = math.log(1 + float(doc_num) / (cnt + 1), 2)

    return phrase_idf