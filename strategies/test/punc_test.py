import sys
sys.path.append('/Users/steve/github/phrasemining/phrasemining/strategies')

from utils.extract_punc import PuncPortion



def calc_punc_portion(doc, freq_data):
  punc_portion = PuncPortion(freq_data, doc)
  print punc_portion.compute_punc_portion()

def main():
  doc1 = '1.txt'
  phrase_cnt = {'a bc de':1, 'a b cde':1, 'ab cd ef':1, 'abc def gh':1, 'cc d dd':1, 'abc ef':1}
  freq_data = {0:phrase_cnt}

  calc_punc_portion(doc1, freq_data)


if __name__ == '__main__':
  main()