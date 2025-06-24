# Evaluation

The evaluation pipeline includes three stages:

1. **Data Preparation**  
 Merges and formats model-generated code with metadata and aligns ground truth–synthetic pairs.

2. **Feature Extraction**  
 Extracts functionality, style, and embedding metrics.

3. **Data Analysis**  
 Analyzes and visualizes the feature-extracted data.


---

## Scripts and Pipeline 
Note: `data/` is empty because we do not release data. However, if you run the scripts in the listed order using your own generated data, you will reproduce the same structure.

### Data Preparation
1. `scripts/merge.py`: Merges generated code with metadata → `data/formatted/`
2. `scripts/format.py`: Formats data into GT–synthetic pairs → `data/merged/`

### Feature Extraction
3. `scripts/generate_doctests.py`: Extracts doctests from each problem statement → `doc_tests/`
4. `scripts/test_classify.py`: Classifies problems as `test_NS_OP` (test1) or `test_NS_NP` (test3). Test2 and test4 were not explored on the paper due to no significant result difference → `test_class/`
5. `scripts/add_metrics.py`: Main script to compute style and functionality metrics (calls `autograder.py`).  
 Input: `--input_dir`; Output: `--output_dir` with feature-augmented files.
6. `scripts/embed_codes.py`: Generates code embeddings  → `data/formatted_embeddings`
7. `scripts/merge_features.py`: Combines extracted metrics and embeddings → `data/with_features_with_embeddings/`

### Data Analysis
8. Run `results_sec.ipynb` to reproduce the plots on the paper


