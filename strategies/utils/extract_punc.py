from utils import agg_phrase_cnt
import codecs

class PuncPortion:
  def __init__(self, freq_data, parsed_file, selected_doc=None):
    self.phrase_cnt = agg_phrase_cnt(freq_data, selected_doc)
    self.parsed_file = parsed_file
    self.selected_doc = selected_doc

  def cnt_punc(self):
    phrase_punc_cnt = {}

    doc_index = -1
    with codecs.open(self.parsed_file, "r") as f:
      for doc in f:
        doc_index += 1
        if self.selected_doc is not None and doc_index not in self.selected_doc:
          continue

        bracket_cnt = 0
        is_in_phrase = False
        is_in_quote = False

        for ch in doc:
          if ch == "\"":
            is_in_quote = not is_in_quote
          if ch == "[":
            phrase = ""
            is_in_phrase = True
            connected_by_dash = True
            bracket_cnt += 1
          elif ch == "]":
            bracket_cnt -= 1
            phrase = phrase.strip()
            if phrase != "":
              if bracket_cnt > 0 or is_in_quote or connected_by_dash:
                if phrase not in phrase_punc_cnt:
                  phrase_punc_cnt[phrase] = 0
                phrase_punc_cnt[phrase] += 1
            
            is_in_phrase = False
            phrase = ""
          else:
            if is_in_phrase == True:
              if ch.isalpha():
                phrase += ch.lower()
              elif ch == "'":
                phrase += ch
              else:
                if ch != '-':
                  connected_by_dash = False
                phrase += " "

    return phrase_punc_cnt


  def compute_punc_portion(self):
    phrase_punc_portion = {}
    punc_cnt = self.cnt_punc()
    for phrase in self.phrase_cnt:
      if phrase not in punc_cnt:
        phrase_punc_portion[phrase] = float(0)
      else:
        phrase_punc_portion[phrase] = float(punc_cnt[phrase]) / self.phrase_cnt[phrase]

    return phrase_punc_portion






      