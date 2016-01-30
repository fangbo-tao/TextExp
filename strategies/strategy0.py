from utils.extract_freq_portion import FreqPortion as FreqPortion
from utils.extract_idf import IDFMeasure as IDFMeasure
from utils.extract_cap import CapPortion as CapPortion
from utils.extract_punc import PuncPortion as PuncPortion
from utils.extract_mi_kl import InfoTheoryFeatures as MIKL
from utils.utils import load_simple_measure as load_freq
from utils.utils import load_frequent_patterns as load_freq_patterns
from utils.utils import save_dict_list as save_phrase_features
from utils.utils import load_cube as load_cube
from utils.utils import normalize_feature

import sys
import codecs

class FeatureExtractor:

  def __init__(self, parsed_file, selected_doc, freq_data, stop_word_file, freq_patterns):
    self.parsed_file = parsed_file
    self.selected_doc = selected_doc
    self.freq_data = freq_data
    self.stop_word_file = stop_word_file
    self.freq_patterns = freq_patterns


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

    return [phrase_freq, phrase_idf, phrase_cap_portion, phrase_punc_portion, phrase_mi, phrase_kl]


  def extract_features(self):
    phrase_fea_dict_list = self.do_extract()
    phrase_feature_list = self.agg(phrase_fea_dict_list)

    return phrase_feature_list


def save_features(out_file, phrase_feature_dict):
  with codecs.open(out_file, "w+", encoding="utf-8") as f:
    f.write('pattern,freq,idf,cap,punc,mi,kl\n')
    for phrase, fea_list in phrase_feature_dict.items():
      wline = u"{0},{1}\n".format(phrase, ",".join(map(str, fea_list)))
      f.write(wline)

def extract_features(parsed_file, cube_file, freq_data_file, stop_word_file, freq_pattern_file, base_dir, total_docs):
  freq_patterns = load_freq_patterns(freq_pattern_file)
  freq_data = load_freq(freq_data_file)
  cubes = load_cube(cube_file)
  cubes['all'] = [i for i in range(total_docs)]

  #extract the features of phrases in each cube
  for att in cubes:
    selected_doc = cubes[att]
    feature_extractor = FeatureExtractor(parsed_file, selected_doc, freq_data, stop_word_file, freq_patterns)
    phrase_features = feature_extractor.extract_features()

    file_name = "{0}/{1}.fea".format(base_dir, att.replace('|', '_').replace(';', '_').replace(' ', '_'))
    save_features(file_name, phrase_features)

if __name__ == "__main__":
  if len(sys.argv) < 8:
    print "<usage> [parsed file] [cube file] [freq data file] [stop word file] [freq pattern file] [base dir] [#docs]"
    sys.exit(-1)

  extract_features(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], int(sys.argv[7]))
