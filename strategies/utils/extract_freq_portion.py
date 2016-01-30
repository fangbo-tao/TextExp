from utils import agg_phrase_cnt

class FreqPortion:
  def __init__(self, freq_data, selected_doc=None):
    self.freq_data = freq_data
    self.selected_doc = selected_doc

  def compute_freq_portion(self):
    phrase_freq_portion = agg_phrase_cnt(self.freq_data, self.selected_doc)
    # print phrase_freq_portion

    freq_sum = sum(phrase_freq_portion.values())
    for phrase in phrase_freq_portion:
      phrase_freq_portion[phrase] /= float(freq_sum)

    return phrase_freq_portion