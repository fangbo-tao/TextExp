import sys
sys.path.append('/Users/steve/github/phrasemining/phrasemining/strategies')

from utils.extract_cap import CapPortion



def calc_cap_portion(doc, freq_data):
  cap_portion = CapPortion(freq_data, doc)
  print cap_portion.compute_cap_portion()

def main():
  doc1 = '1.txt'
  phrase_cnt = {'a bc de':1, 'a b cde':1, 'ab cd ef':1, 'abc def gh':1, 'cc d dd':1, 'abc ef':1}
  freq_data = {0:phrase_cnt}

  calc_cap_portion(doc1, freq_data)


if __name__ == '__main__':
  main()