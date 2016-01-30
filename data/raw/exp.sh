# Prepare the data:
python simple_query.py


# Generate features
python strategy1.py ../data/processed/qualified_docs.txt ../data/processed/unified.csv ../data/query/new_hier/cells.txt ../data/query/new_hier/cells_siblings.txt ../data/processed/pure_freq_qualified_newid.txt ../data/raw/stopwords.txt ../data/processed/patterns.csv ../data/feature/strategy1_sibling_flat 41959 "Topic|Business;Location|China;"

# Generate training data
python auto_cell_label_generation.py ../data/feature/strategy1_sibling_flat/cells.fea.fea auto.cell.fancy.label

# Train with Random Forestsh
./bin/predict_quality phrasemining/data/feature/strategy1_sibling_flat/cells.fea.fea phrasemining/data/train/auto.cell.fancy.label phrasemining/data/processed/ranking_cell.csv frequency 0 TRAIN results_case_study/random_forest_1.model


./segphrase/predict_quality data/feature/strategy1_sibling_flat/cells.fea.fea data/train/auto.cell.fancy.label data/processed/ranking_cell.csv frequency 0 TRAIN data/temp/random_forest_1.model



# MCX related

# pre pre process
python mcx.py prepreprocess ../data/raw/docs.txt ../data/mcx/pure_freq_mcx.txt ../data/raw/stopwords.txt

python mcx.py preprocess ../data/mcx/pure_freq_mcx.txt ../data/mcx/mcx_unified_basic.txt ../data/mcx/forward_map_basic.txt


python mcx.py rank ../data/mcx/mcx_unified_basic.txt ../data/mcx/forward_map_basic.txt ../data/query/new_hier/cells.txt ../data/mcx/phrase_rank_mcx_basic.txt 41959 "Topic|Business;Location|China;"

# preprocess the phrase list
python mcx.py preprocess ../data/processed/pure_freq_qualified_newid.txt ../data/mcx/mcx_unified_sp.txt ../data/mcx/forward_map_sp.txt

# rank phrases given cell
python mcx.py rank ../data/mcx/mcx_unified_sp.txt ../data/mcx/forward_map_sp.txt ../data/query/new_hier/cells.txt ../data/mcx/phrase_rank_mcx.txt 41959 "Topic|Business;Location|China;"






# pairwise classification
python pairwise_classification.py ../data/raw/docs.txt ../data/exp/pairs.txt ../data/exp/top_phrases.txt

python pairwise_classification.py ../data/raw/docs.txt ../data/exp/pairs_olaporp.txt ../data/exp/top_phrases_olaporp.txt

python pairwise_classification.py ../data/raw/docs.txt ../data/exp/pairs_OLAPORP_ALL.txt ../data/exp/top_phrases_OLAPORP_ALL.txtnounigram
