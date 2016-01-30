import sys
from random import shuffle
from math import sqrt

if len(sys.argv) != 3:
    print '[usage] <feature table> <generated label>'
    sys.exit(-1)

feature_table = sys.argv[1]
generated_label = sys.argv[2]

def normalizeMatrix(matrix):
    for i in xrange(dimension):
        sum = 0
        sum2 = 0;
        for j in xrange(len(matrix)):
            sum += matrix[j][i]
            sum2 += matrix[j][i] * matrix[j][i]
        avg = sum / len(matrix)
        avg2 = sum2 / len(matrix)
        variance = avg2 - avg * avg
        stderror = sqrt(variance)
        for j in xrange(len(matrix)):
            matrix[j][i] = (matrix[j][i] - avg)
            if stderror > 1e-8:
                matrix[j][i] /= stderror
    return matrix

X = np.random.rand(10, 10)
X = np.tril(X) + np.tril(X, -1).T

# loading
dimension = 0
matrixWiki = []
phraseWiki = []
matrixOther = []
phraseOther = []
labels = []

for line in open(feature_table, 'r'):
    tokens = line.split(',')
    if tokens[0] == 'pattern':
        attributes = tokens
        #print attributes
        continue
    coord = []
    for coor in xrange(1, len(tokens)):
        coord.append(float(tokens[coor]))
    if coord[0] > 0.008 and coord[6] > 0.7 and coord[7] > 0.9:
        phraseWiki.append(tokens[0])
    else:
        phraseOther.append(tokens[0])

print len(phraseWiki)
print len(phraseOther)
min_ = min(len(phraseWiki), len(phraseOther))
min_ = min(min_, 50)
shuffle(phraseWiki)
shuffle(phraseOther)
for i in range(min_):
    labels.append(phraseWiki[i] + '\t1\n')

for i in range(min_):
    labels.append(phraseOther[i] + '\t0\n')

        
out = open(generated_label, 'w')
out.write(''.join(labels))
out.close()


