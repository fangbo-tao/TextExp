import sys
from sklearn import linear_model
from os import listdir
import numpy as np
import codecs
from utils import get_train_data
from utils import load_features



def train(fea_file, pos_file, neg_file):
  X, y = get_train_data(pos_file, neg_file, fea_file)
  model = linear_model.LogisticRegression(C=0.1, penalty = 'l2')

  model.fit(X, y)
  return model

def save_result(items, of):
  with codecs.open(of, "w+", encoding="utf-8") as f:
    for score, phrase in items:
      f.write("{0}\t{1}\n".format(phrase, score))

def save_model(model, model_file):
  weights = model.coef_
  intercept = model.intercept_
  with open(model_file, "w+") as f:
    f.write("weights: ")
    f.write(str(weights.tolist()))
    f.write("\n")
    f.write("intercept: ")
    f.write(str(intercept.tolist()))

def main(fea_dir, pos_file, neg_file, out_dir, model_file):
  model = train("{0}/all.fea".format(fea_dir), pos_file, neg_file)
  if save_model != None:
    save_model(model, model_file)

  for f in listdir(fea_dir):
    #if f == "all.fea":
    #  continue
    
    file_path = "{0}/{1}".format(fea_dir, f)
    ph_fea = load_features(file_path)

    phrase_list = []
    fea_list = []

    for ph in ph_fea:
      phrase_list.append(ph)
      fea_list.append(ph_fea[ph])

    X = np.asarray(fea_list)
    scores = model.decision_function(X)

    items = [(scores[i], phrase_list[i]) for i in range(len(phrase_list))]
    items.sort(reverse=True)

    save_result(items, "{0}/{1}".format(out_dir, f))


if __name__ == "__main__":
  if len(sys.argv) < 5:
    print "<usage> [feature dir] [pos file] [neg file] [out dir] [model_file]"
    sys.exit(-1)

  main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
