import codecs
import numpy as np

def load_phrases(phrase_file):
  phrases = []
  with codecs.open(phrase_file, "r", encoding="utf-8") as f:
    for line in f:
      phrases.append(line.strip())

  return phrases

def load_features(fea_file):
  phrase_fea = {}
  with codecs.open(fea_file, "r", encoding="utf-8") as f:
    for line in f:
      arr = line.strip().split("\t")
      ph = " ".join(arr[0].strip().split())
      feas = [float(s) for s in arr[1:]]

      phrase_fea[ph] = feas

  return phrase_fea

def get_train_data(pos_file, neg_file, fea_file):
  phrase_fea = load_features(fea_file)
  pos_ph_list = load_phrases(pos_file)
  neg_ph_list = load_phrases(neg_file)

  nrow = len(pos_ph_list) + len(neg_ph_list)
  ncol = len(phrase_fea.values()[0])

  X = np.zeros(shape=(nrow, ncol))
  y = np.zeros(shape=(nrow,))

  i = 0
  for pos_ph in pos_ph_list:
    print pos_ph
    X[i] = np.asarray(phrase_fea[pos_ph])
    y[i] = 1

    i += 1

  for neg_ph in neg_ph_list:
    X[i] = np.asarray(phrase_fea[neg_ph])
    y[i] = 0

    i += 1

  return X, y
