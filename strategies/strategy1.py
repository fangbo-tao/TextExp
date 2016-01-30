from utils.extract_freq_portion import FreqPortion as FreqPortion
from utils.extract_idf import IDFMeasure as IDFMeasure
from utils.extract_cap import CapPortion as CapPortion
from utils.extract_punc import PuncPortion as PuncPortion
from utils.extract_mi_kl import InfoTheoryFeatures as MIKL
from utils.extract_context_freq import ContextFreq
from utils.extract_context_score_fancy import ContextScore
from utils.extract_context_freq_distribution import ContextFreqDist
from utils.utils import load_simple_measure as load_freq
from utils.utils import load_frequent_patterns as load_freq_patterns
from utils.utils import save_dict_list as save_phrase_features
from utils.utils import load_cube as load_cube
from utils.utils import load_context as load_context
from utils.utils import load_unified_list
from utils.utils import normalize_feature
from utils.utils import agg_phrase_cnt
from utils.utils import normalize

import sys
import codecs

class FeatureExtractor:

  def __init__(self, parsed_file, selected_doc, selected_context, freq_data, stop_word_file, freq_patterns, total_cnt, global_scores):
    self.parsed_file = parsed_file
    self.selected_doc = selected_doc
    self.selected_context = selected_context
    self.freq_data = freq_data
    self.stop_word_file = stop_word_file
    self.freq_patterns = freq_patterns
    self.total_cnt = total_cnt
    self.global_scores = global_scores


  def extract_phrase(self, phrase_fea_list):
    phrase_dict = {}
    for phrase_score in phrase_fea_list:
      for phrase in phrase_score:
        phrase_dict[phrase] = 1

    return phrase_dict

  def agg(self, phrase_fea_list):
    phrase_dict = self.extract_phrase(phrase_fea_list)
    phrase_agg_fea = {}

    for phrase in phrase_dict:
      agg_fea_list = []
      discard = False
      for phrase_score in phrase_fea_list:
        if phrase not in phrase_score or phrase_score[phrase] == -1:
          #print u"[Strategy0.py:agg] Phrase {0} missed some features and thus will be discarded.".format(phrase)
          discard = True
          break
        else:
          agg_fea_list.append(phrase_score[phrase])

      if discard is False:
        phrase_agg_fea[phrase] = agg_fea_list

    return phrase_agg_fea


  def do_extract(self):
    freq_port = FreqPortion(self.freq_data, self.selected_doc)
    phrase_freq = freq_port.compute_freq_portion()
    normalize_feature(phrase_freq)

    context_freq = ContextFreq(self.freq_data, self.selected_doc, self.selected_context, self.total_cnt)
    phrase_context_freq = context_freq.compute_context_freq()
    normalize_feature(phrase_context_freq)
    
    context_freq = ContextScore(self.freq_data, self.selected_doc, self.selected_context, self.total_cnt, self.global_scores)
    phrase_context_freq = context_freq.compute_context_score()
    #normalize_feature(phrase_context_freq)
    

    idf = IDFMeasure(self.freq_data, self.selected_doc)
    phrase_idf = idf.compute_idf()
    normalize_feature(phrase_idf)    

    cap = CapPortion(self.freq_data, self.parsed_file, self.selected_doc)
    phrase_cap_portion = cap.compute_cap_portion()
    normalize_feature(phrase_cap_portion)

    punc = PuncPortion(self.freq_data, self.parsed_file, self.selected_doc)
    phrase_punc_portion = punc.compute_punc_portion()
    normalize_feature(phrase_punc_portion)

    mi_kl = MIKL(self.freq_patterns, self.freq_data, self.selected_doc)
    phrase_mi, phrase_kl = mi_kl.compute_mi_and_kl()
    normalize_feature(phrase_mi)
    normalize_feature(phrase_kl)

    # Experimental
    #context_freq_dist = ContextFreqDist(self.freq_data, self.selected_doc, self.selected_context, self.total_cnt)
    #phrase_context_freq_dist = context_freq_dist.compute_context_freq_dist()



    return [phrase_freq, phrase_idf, phrase_cap_portion, phrase_punc_portion, phrase_mi, phrase_kl, phrase_context_freq]
    #[phrase_context_freq_dist, phrase_freq, phrase_idf, phrase_cap_portion, phrase_punc_portion, phrase_mi, phrase_kl, phrase_context_freq]


  def extract_features(self):
    phrase_fea_dict_list = self.do_extract()
    phrase_feature_list = self.agg(phrase_fea_dict_list)

    return phrase_feature_list


def save_features(out_file, phrase_feature_dict):
  with codecs.open(out_file, "w+", encoding="utf-8") as f:
    f.write('pattern,freq,idf,cap,punc,mi,kl,context_freq,global_score\n')
    for phrase, fea_list in phrase_feature_dict.items():
      wline = u"{0},{1}\n".format(phrase, ",".join(map(str, fea_list)))
      f.write(wline)

def extract_features(parsed_file, unified_file, cube_file, cube_context_file, freq_data_file, stop_word_file, freq_pattern_file, base_dir, total_docs, filtered_cell_str):
  print filtered_cell_str
  freq_patterns = load_freq_patterns(freq_pattern_file)
  freq_data = load_freq(freq_data_file)
  cubes = load_cube(cube_file)
  contexts = load_context(cube_context_file)
  unified_list = load_unified_list(unified_file)
  print contexts.keys()
  #cubes['all'] = [i for i in range(total_docs)]
  all_docs = [i for i in range(total_docs)]
  total_cnt = agg_phrase_cnt(freq_data, all_docs)

  print sum(total_cnt.values())
 
  #extract the features of phrases in each cube
  phrase_feature_all = {}
  idx = 0
  for att in cubes:
    if att != filtered_cell_str: #'Topic|Sports;Location|Illinois;':
      continue
    print "start processing " + att
    selected_doc = cubes[att]
    selected_context = contexts[att]
    #print selected_context
    feature_extractor = FeatureExtractor(parsed_file, selected_doc, selected_context, freq_data, stop_word_file, freq_patterns, total_cnt, unified_list)
    phrase_features = feature_extractor.extract_features()
    for phrase in phrase_features:
      norm_phrase = normalize(phrase)
      phrase_features[phrase].append(unified_list[norm_phrase])
      cell_phrase = "{0}{1}".format(att.replace('|', '_').replace(';', '_').replace(' ', '_').lower(), norm_phrase)
      phrase_feature_all[cell_phrase] = phrase_features[phrase]

  file_name = "{0}/{1}.fea".format(base_dir, "cells.fea")
  save_features(file_name, phrase_feature_all)

if __name__ == "__main__":
  if len(sys.argv) < 8:
    print "<usage> [parsed file] [unfied list file] [cube file] [cube context file] [freq data file] [stop word file] [freq pattern file] [base dir] [#docs] [Cell Str]"
    sys.exit(-1)

  extract_features(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], int(sys.argv[9]), sys.argv[10])
