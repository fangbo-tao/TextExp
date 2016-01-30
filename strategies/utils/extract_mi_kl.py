from utils import extract_phrases
import math

class InfoTheoryFeatures:
  def __init__(self, freq_patterns, freq_data, selected_doc):
    self.freq_patterns = freq_patterns
    self.total_cnt = sum(freq_patterns.values())
    self.phrase_dict = extract_phrases(freq_data, selected_doc)

  def compute_mi_and_kl(self):
    phrase_mi = {}
    phrase_kl = {}
    for phrase in self.phrase_dict:
      ph_arr = phrase.strip().split()
      score = -1
      if len(ph_arr) >= 2:
        for i in range(1, len(ph_arr)):
          ph_left = " ".join(ph_arr[0:i])
          ph_right = " ".join(ph_arr[i:])
          ph = " ".join(ph_arr)

          if ph in self.freq_patterns:
            p_ph = float(self.freq_patterns[ph]) / self.total_cnt
            if ph_left in self.freq_patterns and ph_right in self.freq_patterns:
              p_left = float(self.freq_patterns[ph_left]) / self.total_cnt
              p_right = float(self.freq_patterns[ph_right]) / self.total_cnt
              temp_score = math.log(p_ph / (p_left * p_right))

              if score == -1 or temp_score < score:
                score = temp_score
            else:
              #print u"[ERROR]: {0} in frequent patterns but {1} or {2} not!".format(ph, ph_left, ph_right)
              pass
          else:
            #print u"[ERROR]: {0} NOT in frequent patterns!".format(ph)
            pass

        if score != -1:
          phrase_mi[phrase] = score
          phrase_kl[phrase] = score * p_ph

    return phrase_mi, phrase_kl
