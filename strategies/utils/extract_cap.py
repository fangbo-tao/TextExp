from utils import agg_phrase_cnt
import codecs

class CapPortion:
  def __init__(self, freq_data, parsed_file, selected_doc=None):
    self.phrase_cnt = agg_phrase_cnt(freq_data, selected_doc)
    self.parsed_file = parsed_file
    self.selected_doc = selected_doc

  def cnt_cap(self):
    phrase_cap_cnt = {}

    doc_index = -1
    with codecs.open(self.parsed_file, "r") as f:
      for doc in f:
        doc_index += 1
        if self.selected_doc is not None and doc_index not in self.selected_doc:
          continue

        is_in_phrase = False
        is_all_cap = True
        met_space = True

        for ch in doc:
          if ch == "[":
            phrase = ""
            is_in_phrase = True
            is_all_cap = True
            met_space = True
          elif ch == "]":
            phrase = phrase.strip()
            if phrase != "" and is_all_cap:
              if phrase not in phrase_cap_cnt:
                phrase_cap_cnt[phrase] = 0
              phrase_cap_cnt[phrase] += 1

              is_in_phrase = False
              phrase = ""

          else:
            if is_in_phrase == True:
              if ch.isalpha():
                if met_space == True:
                  if not ch.isupper():
                    is_all_cap = False
                phrase += ch.lower()
              elif ch == "'":
                phrase += ch
              else:
                phrase += " "

              if ch == " ":
                met_space = True
              else:
                met_space = False

    return phrase_cap_cnt

  def compute_cap_portion(self):
    phrase_cap_portion = {}
    cap_cnt = self.cnt_cap()
    for phrase in self.phrase_cnt:
      if phrase not in cap_cnt:
        phrase_cap_portion[phrase] = float(0)
      else:
        phrase_cap_portion[phrase] = float(cap_cnt[phrase]) / self.phrase_cnt[phrase]

    return phrase_cap_portion






      