# phrasemining
The repo for phrase mining project

# how to use
1. construct cell by attribute values
use the ~/phrasemining/baselinecode/query/simple_query.py file. check the file and you'll know how to use it. It's really simple.

2. train on cell level
python train_on_cell.py /srv/data/olap_pm/10_05/phraseminig/data/raw/cubes.txt /srv/data/olap_pm/10_05/ /srv/data/olap_pm/10_05/phraseminig/phrasemining/casestudy/train_on_cell_data/src/ /srv/data/olap_pm/10_05/phraseminig/phrasemining/casestudy/train_on_cell_data/result/

To check out the what the args really are in the command, just type
python train_on_cell.py

3. logistic regress training and testing
python logistic_regression.py ../../../data/features/ ../../../data/train/pos.txt ../../../data/train/neg.txt ../../../result/ ../../../models/0.model

To check out the what the args really are in the command, just type
python logistic_regression.py

4. how to extract features for strategy 0
python strategy0.py ../../data/raw/qualified_docs.txt ../../data/raw/cubes.txt ../../data/raw/pure_freq_qualified_newid.txt ../../data/raw/stopwords.txt ../../data/raw/patterns.csv ../../data/feature1 41959

python strategy1.py ../data/processed/qualified_docs.txt ../data/processed/unified.csv ../data/query/cells.txt ../data/query/cells_parents.txt ../data/processed/pure_freq_qualified_newid.txt ../data/raw/stopwords.txt ../data/processed/patterns.csv ../data/feature/strategy1 41959

python auto_cell_label_generation.py /srv/data/olap_pm/10_05/phraseminig/data/feature2/cells.fea.fea ../../data/train/cell.label.strategy1


To check out the what the args really are in the command, just type
python strategy0.py

5. feature extraction functions are located mostly in utils.py files (there are multiple of them). If you are curious or for debugging case, you can check them out. 

6. Others
other functions such as extract_cases.py are for constructing cell training docs. 

python extract_cases.py /srv/data/olap_pm/10_05/results/unified.csv /srv/data/olap_pm/10_05/phraseminig/data/raw/cubes.txt /srv/data/olap_pm/10_05/phraseminig/data/raw/qualified_docs.txt /srv/data/olap_pm/10_05/phraseminig/phrasemining/casestudy/train_on_cell_data/result_temp

Baseline code will be added in the future.

7. Use Random Forest as classifier
./bin/predict_quality phraseminig/data/feature2/all.fea phraseminig/data/train/cell.label.strategy0 results_case_study/ranking.csv frequency 0 TRAIN results_case_study/random_forest_0.model

./bin/predict_quality phraseminig/data/feature2/cells.fea.fea phraseminig/data/train/cell.label.strategy1 results_case_study/ranking.csv frequency 0 TRAIN results_case_study/random_forest_1.model

# important files
run2.sh: the script to run SegPhrase


