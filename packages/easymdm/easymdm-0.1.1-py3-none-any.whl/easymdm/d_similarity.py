"""This module processes similarity calculations for data records using configurations defined in a YAML file.""" # pylint: disable=line-too-long
import yaml # pylint: disable=import-error
import recordlinkage # pylint: disable=import-error
# from fuzzywuzzy import fuzz
import pandas as pd # pylint: disable=import-error
def process_similarity(df, yaml_path, candidate_pairs):
    """ Process similarity calculations for data records."""
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    similarity_configs = config['similarity']
    thresholds = config['thresholds']
    # 3. Pairwise similarity
    compare = recordlinkage.Compare()
    for sim in similarity_configs:
        column = sim['column']
        method = sim['method']
        if method == 'exact':
            compare.exact(column, column, label=f"{column}_match")
        else:
            compare.string(column, column, method=method, label=f"{column}_sim")

    # Use the MultiIndex directly, not the DataFrame conversion
    features = compare.compute(candidate_pairs, df, df)

    # # Debug missing pairs
    # missing_pairs = [(0, 1), (3, 4)]
    # for pair in missing_pairs:
    #     if pair in features.index:
    #         # print(f"Detailed similarity for {pair}:\n", features.loc[pair].to_dict())
    #         pass
    #     else:
    #         print(f"Pair {pair} not in candidate pairs.")

    # 4. Calculate score
    similarity_labels = [f"{sim['column']}_{'match' if sim['method'] == 'exact' else 'sim'}" for sim in similarity_configs] # pylint: disable=line-too-long
    features['score'] = features[similarity_labels].mean(axis=1)

    # 5. Categorize based on thresholds
    features['match_category'] = pd.cut(
        features['score'],
        bins=[0, thresholds['review'], thresholds['auto_merge'], 1.0],
        labels=['non_match', 'review', 'auto_merge']
    )
    return features
