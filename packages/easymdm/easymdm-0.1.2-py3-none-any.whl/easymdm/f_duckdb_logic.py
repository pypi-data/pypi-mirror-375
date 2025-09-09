import os
import yaml
import duckdb
from datetime import datetime
import time
import hashlib
import pandas as pd
# from jellyfish import jaro_winkler_similarity

def load_duckdb_data(yaml_path, out_path):
    try:
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)

        duck_cfg = config['duckdb'][0]
        DB_PATH = duck_cfg['DB_PATH']
        DB_NAME = duck_cfg['DB_NAME']
        TABLE_NAME = duck_cfg['TABLE_NAME']

        full_db_path = os.path.join(DB_PATH, DB_NAME)

        blocking_columns = config['blocking']['columns']
        blocking_threshold = config['blocking'].get('threshold', [0.8])[0]
        similarity_configs = config['similarity']
        
        if 'thresholds' not in config:
            review_input = input("Enter review threshold (default 0.8): ") or "0.8"
            auto_merge_input = input("Enter auto merge threshold (default 0.9): ") or "0.9"
            thresholds = {'review': float(review_input), 'auto_merge': float(auto_merge_input)}
        else:
            thresholds = config['thresholds']
        
        survivorship = config.get('survivorship', {})
        survivorship_rules = survivorship.get('rules', [])
        priority_rule = config.get('priority_rule', {})
        priority_conditions = priority_rule.get('conditions', [])
        
        has_survivorship = bool(survivorship_rules)
        has_priority_rule = bool(priority_conditions)
        
        if not has_survivorship and not has_priority_rule:
            print("⚠️ Both 'survivorship' and 'priority_rule' blocks are missing. Please define at least one.")
        
        # print("Configuration Status:")
        if has_priority_rule and has_survivorship:
            print("✅ Both priority_rule and survivorship blocks found")
        elif has_priority_rule:
            print("⚠️ Only priority_rule block found")
        elif has_survivorship:
            print("⚠️ Only survivorship block found")
        else:
            print("⚠️ No rules defined - will pick min record_id in case of ties")

        unique_id_cfg = config.get('unique_id', {})
        unique_id_columns = unique_id_cfg.get('columns', [])
        if not unique_id_columns:
            response = input("Unique ID columns not provided. Enter comma-separated column names or press Enter to skip: ")
            if response.strip():
                unique_id_columns = [c.strip() for c in response.split(',')]
            else:
                unique_id_columns = []

        con = duckdb.connect(database=full_db_path, read_only=False)

        # Debug: Print table contents
        # print("Input Data:")
        # input_data = con.execute(f"SELECT * FROM {TABLE_NAME}").df()
        # print(input_data)

        blocking_start_time = time.time()
        concat_expr = " || ' ' || ".join(f"TRIM(LOWER(CAST({c} AS VARCHAR)))" for c in blocking_columns)
        con.execute(f"""
            CREATE OR REPLACE TEMP TABLE temp_blocking AS
            SELECT row_number() OVER () AS record_id, *,                
                   ({concat_expr}) AS full_name
            FROM {TABLE_NAME}
        """)
        # source, firstname, lastname, address, city, zip, phone, email, original, last_updated,
        
        # Debug: Print concatenated strings
        # blocking_data = con.execute("SELECT record_id, full_name FROM temp_blocking").df()
        # print("Blocking Concatenated Strings:")
        # print(blocking_data)
        # if len(blocking_data) >= 2:
        #     str1 = blocking_data['full_name'].iloc[0]
        #     str2 = blocking_data['full_name'].iloc[1]
        #     print(f"Jaro-Winkler Similarity: {jaro_winkler_similarity(str1, str2)}")

        con.execute(f"""
            CREATE OR REPLACE TEMP TABLE candidate_pairs AS
            SELECT a.record_id AS first, b.record_id AS second
            FROM temp_blocking a
            JOIN temp_blocking b ON a.record_id < b.record_id
            WHERE jaro_winkler_similarity(a.full_name, b.full_name) > {blocking_threshold}
        """)
        
        # Debug: Print candidate pairs
        # pairs = con.execute("SELECT * FROM candidate_pairs").df()
        # print("Candidate Pairs:")
        # print(pairs)

        sim_exprs = []
        sum_sim_parts = []
        n_sims = len(similarity_configs)
        for sim_cfg in similarity_configs:
            col = sim_cfg['column']
            method = sim_cfg['method']
            if method == 'jarowinkler':
                expr = f"jaro_winkler_similarity(a.{col}, b.{col}) AS sim_{col}"
            elif method == 'exact':
                expr = f"(a.{col} = b.{col})::DOUBLE AS sim_{col}"
            elif method == 'levenshtein':
                expr = f"1.0 - (levenshtein(a.{col}, b.{col}) / GREATEST(LENGTH(COALESCE(a.{col}, '')), LENGTH(COALESCE(b.{col}, '')))::DOUBLE) AS sim_{col}"
            else:
                expr = f"jaro_winkler_similarity(a.{col}, b.{col}) AS sim_{col}"
            sim_exprs.append(expr)
            sum_sim_parts.append(f"sim_{col}")

        sim_columns_sql = ', '.join(sim_exprs)
        overall_sim_expr = f"CASE WHEN {n_sims} > 0 THEN ({' + '.join(sum_sim_parts)}) / {n_sims} ELSE 0 END AS overall_sim"

        pair_sim_query = f"""
        CREATE OR REPLACE TEMP TABLE pair_similarities AS
        SELECT p.first, p.second, {sim_columns_sql}, {overall_sim_expr}
        FROM candidate_pairs p
        JOIN temp_blocking a ON a.record_id = p.first
        JOIN temp_blocking b ON b.record_id = p.second
        """
        con.execute(pair_sim_query)

        # Debug: Print similarities
        # sim_debug = con.execute(f"SELECT first, second, overall_sim, {', '.join(f'sim_{cfg['column']}' for cfg in similarity_configs)} FROM pair_similarities").df()
        # print("Pair Similarities:")
        # print(sim_debug)

        review_threshold = thresholds['review']
        auto_merge_threshold = thresholds['auto_merge']

        con.execute(f"""
        CREATE OR REPLACE TEMP TABLE auto_merge_links AS
        SELECT first, second
        FROM pair_similarities
        WHERE overall_sim >= {auto_merge_threshold}
        """)

        con.execute(f"""
        CREATE OR REPLACE TEMP TABLE review_links AS
        SELECT first, second, overall_sim
        FROM pair_similarities
        WHERE overall_sim >= {review_threshold} AND overall_sim < {auto_merge_threshold}
        """)

        con.execute("""
        CREATE OR REPLACE TEMP TABLE review_records AS
        SELECT DISTINCT first AS record_id FROM review_links
        UNION
        SELECT DISTINCT second AS record_id FROM review_links
        """)

        # Export auto review data to CSV
        export_review_data_to_csv(con, similarity_configs, out_path)
        
        # Export merge/review decision report
        export_merge_review_decision_report(con, similarity_configs, out_path, priority_conditions, survivorship_rules)

        has_clusters = con.execute("SELECT COUNT(*) FROM auto_merge_links").fetchone()[0] > 0
        # Debug:
        # print(f"Has Clusters: {has_clusters}")

        if has_clusters:
            con.execute("""
            CREATE OR REPLACE TEMP TABLE edges AS
            SELECT first AS src, second AS dst FROM auto_merge_links
            UNION ALL
            SELECT second AS src, first AS dst FROM auto_merge_links
            """)

            con.execute("""
            CREATE OR REPLACE TEMP TABLE nodes AS
            SELECT DISTINCT src AS node FROM edges
            UNION
            SELECT DISTINCT dst AS node FROM edges
            """)

            con.execute("""
            CREATE OR REPLACE TEMP TABLE walks AS
            WITH RECURSIVE walks(node, front) AS (
                SELECT node, node AS front
                FROM nodes
                UNION
                SELECT w.node, e.dst AS front
                FROM walks w
                JOIN edges e ON w.front = e.src
            )
            SELECT * FROM walks
            """)

            con.execute("""
            CREATE OR REPLACE TEMP TABLE components AS
            SELECT node, MIN(front) AS cluster_id
            FROM walks
            GROUP BY node
            """)

            con.execute("""
            CREATE OR REPLACE TEMP TABLE cluster_members AS
            SELECT c.cluster_id, t.*
            FROM components c
            JOIN temp_blocking t ON t.record_id = c.node
            ORDER BY c.cluster_id, t.record_id
            """)

            con.execute("""
            CREATE OR REPLACE TEMP TABLE conflicted_records AS
            SELECT record_id FROM review_records
            UNION
            SELECT record_id FROM cluster_members
            """)
        else:
            con.execute("""
            CREATE OR REPLACE TEMP TABLE conflicted_records AS
            SELECT * FROM review_records
            """)

        con.execute("""
        CREATE OR REPLACE TEMP TABLE single_records_table AS
        SELECT *
        FROM temp_blocking
        WHERE record_id NOT IN (SELECT record_id FROM conflicted_records)
        """)

        def pick_survivor(group_df, priority_conds, surv_rules):
            current = group_df.copy()
            # Debug:
            # print(f"\nPicking survivor for cluster: {group_df['record_id'].tolist()}")
            # print(f"Records in cluster:\n{current}")
            for cond in priority_conds:
                col = cond['column']
                val = cond['value']
                matches = current[current[col] == val]
                # Debug:
                # print(f"Applying priority rule: {col} = {val}, Matches: {len(matches)}")
                if len(matches) == 1:  # Only select if exactly one record matches
                    survivor = matches.iloc[0]
                    # Debug:
                    # print(f"Selected by priority rule: {col}")
                    return survivor, f"priority | {col}"
                elif len(matches) > 1:
                    # Debug:
                    # print(f"Multiple records match {col} = {val}, moving to next rule")
                    continue
                else:
                    # Debug:
                    # print(f"No records match {col} = {val}")
                    continue
            logic_parts = []
            for rule in surv_rules:
                col = rule['column']
                strategy = rule['strategy']
                # Debug:
                # print(f"Applying survivorship rule: {col} {strategy}")
                initial_count = len(current)
                if strategy == 'most_recent':
                    try:
                        # Handle both yyyy-mm-dd and mm/dd/yyyy formats
                        current['temp_col'] = pd.to_datetime(current[col], errors='coerce')
                        max_val = current['temp_col'].max()
                        current = current[current['temp_col'] == max_val].drop('temp_col', axis=1)
                        # Debug:
                        # print(f"After most_recent on {col}: {len(current)} records")
                        # Only add to logic if this rule actually reduced the number of records
                        if len(current) < initial_count:
                            logic_parts.append(f"{col} {strategy}")
                    except Exception as e:
                        print(f"Error in most_recent for {col}: {e}")
                elif strategy == 'source_priority':
                    source_order = rule.get('source_order', [])
                    if source_order:
                        prio_map = {src: i for i, src in enumerate(source_order)}
                        current['prio'] = current[col].map(lambda x: prio_map.get(x, len(source_order) + 1))
                        min_prio = current['prio'].min()
                        current = current[current['prio'] == min_prio].drop('prio', axis=1)
                        # Debug:
                        # print(f"After source_priority on {col}: {len(current)} records")
                        # Only add to logic if this rule actually reduced the number of records
                        if len(current) < initial_count:
                            logic_parts.append(f"{col} {strategy}")
                elif strategy == 'longest_string':
                    current['len_col'] = current[col].astype(str).str.len()
                    max_len = current['len_col'].max()
                    current = current[current['len_col'] == max_len].drop('len_col', axis=1)
                    # Debug:
                    # print(f"After longest_string on {col}: {len(current)} records")
                    # Only add to logic if this rule actually reduced the number of records
                    if len(current) < initial_count:
                        logic_parts.append(f"{col} {strategy}")


                elif strategy == 'highest_value':
                    try:
                        initial_count = len(current)
                        # Convert to numeric if needed
                        current[col] = pd.to_numeric(current[col], errors='coerce')
                        max_val = current[col].max()
                        current = current[current[col] == max_val]
                        # Only add to logic if this rule actually reduced the number of records
                        if len(current) < initial_count:
                            logic_parts.append(f"{col} {strategy}")
                    except Exception as e:
                        print(f"Error in highest_value for {col}: {e}")
                        
                elif strategy == 'lowest_value':
                    try:
                        initial_count = len(current)
                        # Convert to numeric if needed
                        current[col] = pd.to_numeric(current[col], errors='coerce')
                        min_val = current[col].min()
                        current = current[current[col] == min_val]  # Fixed syntax error
                        # Only add to logic if this rule actually reduced the number of records
                        if len(current) < initial_count:
                            logic_parts.append(f"{col} {strategy}")
                    except Exception as e:
                        print(f"Error in lowest_value for {col}: {e}")
                        
                elif strategy == 'greater_than_threshold':
                    try:
                        initial_count = len(current)
                        threshold = rule.get('threshold', 0)
                        # Convert to numeric if needed
                        current[col] = pd.to_numeric(current[col], errors='coerce')
                        current = current[current[col] > threshold]
                        # Only add to logic if this rule actually reduced the number of records
                        if len(current) < initial_count:
                            logic_parts.append(f"{col} {strategy} > {threshold}")
                    except Exception as e:
                        print(f"Error in greater_than_threshold for {col}: {e}")
                
                elif strategy == 'less_than_threshold':
                    try:
                        initial_count = len(current)
                        threshold = rule.get('threshold', 0)
                        # Convert to numeric if needed
                        current[col] = pd.to_numeric(current[col], errors='coerce')
                        current = current[current[col] < threshold]
                        # Only add to logic if this rule actually reduced the number of records
                        if len(current) < initial_count:
                            logic_parts.append(f"{col} {strategy} < {threshold}")
                    except Exception as e:
                        print(f"Error in less_than_threshold for {col}: {e}")





                if len(current) == 1:
                    break
            if len(current) == 1:
                survivor = current.iloc[0]
                logic_str = f"survivorship | {' | '.join(logic_parts)}" if logic_parts else "survivorship | none"
                # Debug:
                # print(f"Selected survivor: {survivor['record_id']}, Logic: {logic_str}")
                return survivor, logic_str
            else:
                survivor = current.loc[current['record_id'].idxmin()]
                logic_str = f"survivorship | {' | '.join(logic_parts)} tie_min_id" if logic_parts else "tie_min_id"
                # print(f"Tie, selected min record_id: {survivor['record_id']}, Logic: {logic_str}")
                return survivor, logic_str

        golden_list = []
        single_query = """
        SELECT * EXCLUDE (full_name)
        FROM single_records_table
        """
        single_df = con.execute(single_query).df()
        for _, row in single_df.iterrows():
            d = row.drop('record_id').to_dict()
            d['Record_ID'] = row['record_id']
            d['similar_record_ids'] = ''
            d['logic'] = 'single'
            if unique_id_columns:
                vals = [str(d.get(c, '')) for c in unique_id_columns]
                d['unique_id'] = hashlib.md5('|'.join(vals).encode('utf-8')).hexdigest()
            else:
                d['unique_id'] = ''
            golden_list.append(d)

        if has_clusters:
            cluster_query = """
            SELECT * EXCLUDE (full_name)
            FROM cluster_members
            """
            cluster_df = con.execute(cluster_query).df()
            grouped = cluster_df.groupby('cluster_id')
            for _, group in grouped:
                group_data = group.drop('cluster_id', axis=1)
                survivor_row, logic = pick_survivor(group_data, priority_conditions, survivorship_rules)
                d = survivor_row.drop('record_id').to_dict()
                d['Record_ID'] = survivor_row['record_id']
                similar_ids_list = sorted(group['record_id'].astype(str))
                d['similar_record_ids'] = '|'.join(similar_ids_list)
                d['logic'] = logic
                if unique_id_columns:
                    vals = [str(d.get(c, '')) for c in unique_id_columns]
                    d['unique_id'] = hashlib.md5('|'.join(vals).encode('utf-8')).hexdigest()
                else:
                    d['unique_id'] = ''
                golden_list.append(d)

        if golden_list:
            golden_df = pd.DataFrame(golden_list)
            con.register('golden_temp', golden_df)
            con.execute("DROP TABLE IF EXISTS golden_table")
            con.execute("CREATE TABLE golden_table AS SELECT * FROM golden_temp")
            # Handle output path - if it's a directory, create a filename
            if os.path.isdir(out_path) or out_path.endswith('/') or out_path.endswith('\\'):
                # If out_path is a directory, create a filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"golden_records_{timestamp}.csv"
                full_output_path = os.path.join(out_path, csv_filename)
                # Ensure the directory exists
                os.makedirs(out_path, exist_ok=True)
            else:
                # If out_path includes filename, use it as is
                full_output_path = out_path
                # Only create directory if dirname is not empty and not current directory
                dirname = os.path.dirname(out_path)
                if dirname and dirname != '.' and dirname != '':
                    os.makedirs(dirname, exist_ok=True)
            
            golden_df.to_csv(full_output_path, index=False)
            print(f"✅ Golden records created: {len(golden_df)} records. Saved to 'golden_table' in DuckDB and '{full_output_path}'")
            # Debug: Print golden records
            # print("Golden Records:")
            # print(golden_df)
        else:
            print("⚠️ No golden records generated.")

        blocking_end_time = time.time()
        blocking_duration = blocking_end_time - blocking_start_time
        print(f"Blocking took {blocking_duration:.2f} seconds")

        con.close()
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'con' in locals():
            con.close()
        return False


def export_review_data_to_csv(con, similarity_configs, out_path):
    """
    Export auto review data to CSV file using existing temp tables.
    This function should be called after the main logic has created the review_links temp table.
    
    Args:
        con: Active DuckDB connection with temp tables already created
        similarity_configs: List of similarity configurations from YAML
        out_path (str): Output directory path where CSV will be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("🔍 Exporting auto review data...")

        # Check if review_links table exists and has data
        review_count = con.execute("SELECT COUNT(*) FROM review_links").fetchone()[0]
        
        if review_count == 0:
            print("ℹ️ No records found requiring manual review.")
            return True

        # Extract detailed review data with original record information and similarity scores
        review_data_query = f"""
        SELECT 
            rl.first AS record_id_1,
            rl.second AS record_id_2,
            rl.overall_sim,
            {', '.join(f'ps.sim_{cfg["column"]}' for cfg in similarity_configs)},
            -- First record details
            a.* EXCLUDE (record_id, full_name),
            -- Second record details  
            b.* EXCLUDE (record_id, full_name)
        FROM review_links rl
        JOIN pair_similarities ps ON ps.first = rl.first AND ps.second = rl.second
        JOIN temp_blocking a ON a.record_id = rl.first
        JOIN temp_blocking b ON b.record_id = rl.second
        ORDER BY rl.overall_sim DESC
        """
        
        review_df = con.execute(review_data_query).df()

        # Handle output path - if it's a directory, create a filename
        if os.path.isdir(out_path) or out_path.endswith('/') or out_path.endswith('\\'):
            # If out_path is a directory, create a filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"auto_review_data_{timestamp}.csv"
            full_output_path = os.path.join(out_path, csv_filename)
            # Ensure the directory exists
            os.makedirs(out_path, exist_ok=True)
        else:
            # If out_path includes filename, use it as is but modify to indicate review data
            dirname = os.path.dirname(out_path)
            basename = os.path.basename(out_path)
            name, ext = os.path.splitext(basename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{name}_auto_review_{timestamp}{ext if ext else '.csv'}"
            full_output_path = os.path.join(dirname, csv_filename)
            # Only create directory if dirname is not empty and not current directory
            if dirname and dirname != '.' and dirname != '':
                os.makedirs(dirname, exist_ok=True)
        
        review_df.to_csv(full_output_path, index=False)
        print(f"✅ Auto review data exported: {len(review_df)} record pairs requiring manual review.")
        print(f"📁 Saved to: '{full_output_path}'")
        print(f"📊 Similarity range: {review_df['overall_sim'].min():.3f} - {review_df['overall_sim'].max():.3f}")
        
        return True

    except Exception as e:
        print(f"❌ Error exporting auto review data: {str(e)}")
        return False


def export_merge_review_decision_report(con, similarity_configs, out_path, priority_conditions, survivorship_rules):
    """
    Export a comprehensive CSV report showing records chosen for merge or review,
    their similarity scores, and final decisions made by priority or survivorship rules.
    
    Args:
        con: Active DuckDB connection with temp tables already created
        similarity_configs: List of similarity configurations from YAML
        out_path (str): Output directory path where CSV will be saved
        priority_conditions: List of priority rule conditions
        survivorship_rules: List of survivorship rules
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("📊 Generating merge/review decision report...")

        # Check if we have any merge or review data
        merge_count = con.execute("SELECT COUNT(*) FROM auto_merge_links").fetchone()[0]
        review_count = con.execute("SELECT COUNT(*) FROM review_links").fetchone()[0]
        
        if merge_count == 0 and review_count == 0:
            print("ℹ️ No records found for merge or review - no decision report needed.")
            return True

        decision_records = []

        # Process auto-merge records (clusters) - only if cluster_members table exists
        cluster_exists = False
        try:
            con.execute("SELECT COUNT(*) FROM cluster_members").fetchone()
            cluster_exists = True
        except:
            cluster_exists = False
            
        if merge_count > 0:
            if not cluster_exists:
                print("⚠️ Auto-merge records found but cluster_members table doesn't exist. This indicates an issue with cluster processing.")
                # Still try to process auto-merge records directly from auto_merge_links
                auto_merge_query = f"""
                SELECT 
                    aml.first,
                    aml.second,
                    ps.overall_sim,
                    {', '.join(f'ps.sim_{cfg["column"]}' for cfg in similarity_configs)},
                    -- First record data
                    tb1.* EXCLUDE (record_id, full_name),
                    -- Second record data  
                    tb2.* EXCLUDE (record_id, full_name)
                FROM auto_merge_links aml
                JOIN pair_similarities ps ON ps.first = aml.first AND ps.second = aml.second
                JOIN temp_blocking tb1 ON tb1.record_id = aml.first
                JOIN temp_blocking tb2 ON tb2.record_id = aml.second
                ORDER BY ps.overall_sim DESC
                """
                
                auto_merge_df = con.execute(auto_merge_query).df()
                
                # Get original column names (excluding record_id and full_name)
                original_cols = [col for col in con.execute("SELECT * FROM temp_blocking LIMIT 1").df().columns 
                               if col not in ['record_id', 'full_name']]
                
                for _, row in auto_merge_df.iterrows():
                    record_ids = [row['first'], row['second']]
                    similarity_score = row['overall_sim']
                    
                    # Add both records in the auto-merge pair
                    for i, record_id in enumerate(record_ids):
                        record_data = {
                            'record_id': record_id,
                            'decision_type': 'auto_merge',
                            'cluster_group': '|'.join(map(str, sorted(record_ids))),
                            'similarity_score': similarity_score,
                            'is_survivor': i == 0,  # First record is survivor by default
                            'survivor_logic': 'auto_merge_default' if i == 0 else '',
                            'survivor_record_id': record_ids[0]
                        }
                        
                        # Add individual similarity scores
                        for cfg in similarity_configs:
                            col_name = f'sim_{cfg["column"]}'
                            record_data[col_name] = row.get(col_name, 0.0)
                        
                        # Add original record data
                        for col in original_cols:
                            record_data[col] = row[col] if i == 0 else row[col]
                        
                        decision_records.append(record_data)
            else:
                # Get cluster information with similarity scores
                cluster_query = f"""
                SELECT 
                    c.cluster_id,
                    c.record_id,
                    -- Get similarity scores for pairs within this cluster
                    COALESCE(ps1.overall_sim, ps2.overall_sim) as similarity_score,
                    {', '.join(f'COALESCE(ps1.sim_{cfg["column"]}, ps2.sim_{cfg["column"]}) as sim_{cfg["column"]}' for cfg in similarity_configs)},
                    -- Original record data
                    tb.* EXCLUDE (record_id, full_name)
                FROM cluster_members c
                JOIN temp_blocking tb ON tb.record_id = c.record_id
                LEFT JOIN pair_similarities ps1 ON (ps1.first = c.record_id OR ps1.second = c.record_id)
                LEFT JOIN pair_similarities ps2 ON (ps2.first = c.record_id OR ps2.second = c.record_id)
                ORDER BY c.cluster_id, c.record_id
                """
                
                cluster_df = con.execute(cluster_query).df()
                
                # Group by cluster and determine survivors
                for cluster_id, group in cluster_df.groupby('cluster_id'):
                    # Get all record IDs in this cluster
                    record_ids = sorted(group['record_id'].tolist())
                    
                    # Get the maximum similarity score for this cluster
                    max_similarity = group['similarity_score'].max() if not group['similarity_score'].isna().all() else 0.0
                    
                    # Determine survivor using the same logic as main function
                    group_for_survivor = group.drop(['cluster_id', 'similarity_score'] + [f'sim_{cfg["column"]}' for cfg in similarity_configs], axis=1)
                    survivor_row, logic = pick_survivor_for_report(group_for_survivor, priority_conditions, survivorship_rules)
                    survivor_id = survivor_row['record_id']
                    
                    # Add records to decision list
                    for _, row in group.iterrows():
                        record_data = {
                            'record_id': row['record_id'],
                            'decision_type': 'auto_merge',
                            'cluster_group': '|'.join(map(str, record_ids)),
                            'similarity_score': max_similarity,
                            'is_survivor': row['record_id'] == survivor_id,
                            'survivor_logic': logic if row['record_id'] == survivor_id else '',
                            'survivor_record_id': survivor_id
                        }
                        
                        # Add individual similarity scores
                        for cfg in similarity_configs:
                            col_name = f'sim_{cfg["column"]}'
                            record_data[col_name] = row.get(col_name, 0.0)
                        
                        # Add original record data
                        for col in group_for_survivor.columns:
                            if col != 'record_id':
                                record_data[col] = row[col]
                        
                        decision_records.append(record_data)

        # Process review records
        if review_count > 0:
            review_query = f"""
            SELECT 
                rl.first,
                rl.second,
                rl.overall_sim,
                {', '.join(f'ps.sim_{cfg["column"]}' for cfg in similarity_configs)},
                -- First record data
                tb1.* EXCLUDE (record_id, full_name),
                -- Second record data  
                tb2.* EXCLUDE (record_id, full_name)
            FROM review_links rl
            JOIN pair_similarities ps ON ps.first = rl.first AND ps.second = rl.second
            JOIN temp_blocking tb1 ON tb1.record_id = rl.first
            JOIN temp_blocking tb2 ON tb2.record_id = rl.second
            ORDER BY rl.overall_sim DESC
            """
            
            review_df = con.execute(review_query).df()
            
            # Get original column names (excluding record_id and full_name)
            original_cols = [col for col in con.execute("SELECT * FROM temp_blocking LIMIT 1").df().columns 
                           if col not in ['record_id', 'full_name']]
            
            for _, row in review_df.iterrows():
                record_ids = [row['first'], row['second']]
                similarity_score = row['overall_sim']
                
                # Add both records in the review pair
                for i, record_id in enumerate(record_ids):
                    record_data = {
                        'record_id': record_id,
                        'decision_type': 'manual_review',
                        'cluster_group': '|'.join(map(str, sorted(record_ids))),
                        'similarity_score': similarity_score,
                        'is_survivor': False,  # No survivor chosen yet for review records
                        'survivor_logic': 'pending_manual_review',
                        'survivor_record_id': ''
                    }
                    
                    # Add individual similarity scores
                    for cfg in similarity_configs:
                        col_name = f'sim_{cfg["column"]}'
                        record_data[col_name] = row.get(col_name, 0.0)
                    
                    # Add original record data - need to get from the right record
                    for col in original_cols:
                        # For first record, use columns as-is; for second record, they might have different names
                        record_data[col] = row[col] if i == 0 else row[col]
                    
                    decision_records.append(record_data)

        if decision_records:
            # Create DataFrame and save to CSV
            decision_df = pd.DataFrame(decision_records)
        else:
            print("ℹ️ No decision records were created - this means no merge or review pairs were found.")
            return True
            
        if len(decision_records) > 0:
            
            # Handle output path
            if os.path.isdir(out_path) or out_path.endswith('/') or out_path.endswith('\\'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"merge_review_decisions_{timestamp}.csv"
                full_output_path = os.path.join(out_path, csv_filename)
                os.makedirs(out_path, exist_ok=True)
            else:
                dirname = os.path.dirname(out_path)
                basename = os.path.basename(out_path)
                name, ext = os.path.splitext(basename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"{name}_merge_review_decisions_{timestamp}{ext if ext else '.csv'}"
                full_output_path = os.path.join(dirname, csv_filename)
                if dirname and dirname != '.' and dirname != '':
                    os.makedirs(dirname, exist_ok=True)
            
            decision_df.to_csv(full_output_path, index=False)
            
            # Print summary statistics
            total_records = len(decision_df)
            merge_records = len(decision_df[decision_df['decision_type'] == 'auto_merge'])
            review_records = len(decision_df[decision_df['decision_type'] == 'manual_review'])
            survivors = len(decision_df[decision_df['is_survivor'] == True])
            
            print(f"✅ Merge/Review decision report exported: {total_records} total records")
            print(f"   📈 Auto-merge records: {merge_records}")
            print(f"   👁️ Manual review records: {review_records}")
            print(f"   🏆 Survivors chosen: {survivors}")
            print(f"📁 Saved to: '{full_output_path}'")
            
            if total_records > 0:
                sim_range = f"{decision_df['similarity_score'].min():.3f} - {decision_df['similarity_score'].max():.3f}"
                print(f"📊 Similarity score range: {sim_range}")
        
        return True

    except Exception as e:
        print(f"❌ Error generating merge/review decision report: {str(e)}")
        return False


def pick_survivor_for_report(group_df, priority_conds, surv_rules):
    """
    Helper function to pick survivor for reporting - mirrors the main pick_survivor logic
    but simplified for reporting purposes.
    """
    current = group_df.copy()
    
    # Priority rules first
    for cond in priority_conds:
        col = cond['column']
        val = cond['value']
        matches = current[current[col] == val]
        if len(matches) == 1:
            survivor = matches.iloc[0]
            return survivor, f"priority | {col}"
        elif len(matches) > 1:
            continue
        else:
            continue
    
    # Survivorship rules
    logic_parts = []
    for rule in surv_rules:
        col = rule['column']
        strategy = rule['strategy']
        initial_count = len(current)
        
        if strategy == 'most_recent':
            try:
                current['temp_col'] = pd.to_datetime(current[col], errors='coerce')
                max_val = current['temp_col'].max()
                current = current[current['temp_col'] == max_val].drop('temp_col', axis=1)
                if len(current) < initial_count:
                    logic_parts.append(f"{col} {strategy}")
            except Exception:
                pass
        elif strategy == 'source_priority':
            source_order = rule.get('source_order', [])
            if source_order:
                prio_map = {src: i for i, src in enumerate(source_order)}
                current['prio'] = current[col].map(lambda x: prio_map.get(x, len(source_order) + 1))
                min_prio = current['prio'].min()
                current = current[current['prio'] == min_prio].drop('prio', axis=1)
                if len(current) < initial_count:
                    logic_parts.append(f"{col} {strategy}")
        elif strategy == 'longest_string':
            current['len_col'] = current[col].astype(str).str.len()
            max_len = current['len_col'].max()
            current = current[current['len_col'] == max_len].drop('len_col', axis=1)
            if len(current) < initial_count:
                logic_parts.append(f"{col} {strategy}")
        elif strategy == 'highest_value':
            try:
                current[col] = pd.to_numeric(current[col], errors='coerce')
                max_val = current[col].max()
                current = current[current[col] == max_val]
                if len(current) < initial_count:
                    logic_parts.append(f"{col} {strategy}")
            except Exception:
                pass
        elif strategy == 'lowest_value':
            try:
                current[col] = pd.to_numeric(current[col], errors='coerce')
                min_val = current[col].min()
                current = current[current[col] == min_val]
                if len(current) < initial_count:
                    logic_parts.append(f"{col} {strategy}")
            except Exception:
                pass
        elif strategy == 'greater_than_threshold':
            try:
                threshold = rule.get('threshold', 0)
                current[col] = pd.to_numeric(current[col], errors='coerce')
                current = current[current[col] > threshold]
                if len(current) < initial_count:
                    logic_parts.append(f"{col} {strategy} > {threshold}")
            except Exception:
                pass
        elif strategy == 'less_than_threshold':
            try:
                threshold = rule.get('threshold', 0)
                current[col] = pd.to_numeric(current[col], errors='coerce')
                current = current[current[col] < threshold]
                if len(current) < initial_count:
                    logic_parts.append(f"{col} {strategy} < {threshold}")
            except Exception:
                pass
        
        if len(current) == 1:
            break
    
    if len(current) == 1:
        survivor = current.iloc[0]
        logic_str = f"survivorship | {' | '.join(logic_parts)}" if logic_parts else "survivorship | none"
        return survivor, logic_str
    else:
        survivor = current.loc[current['record_id'].idxmin()]
        logic_str = f"survivorship | {' | '.join(logic_parts)} tie_min_id" if logic_parts else "tie_min_id"
        return survivor, logic_str


# import os
# import yaml
# import duckdb
# from datetime import datetime
# import time
# import hashlib
# import pandas as pd

# def load_duckdb_data(yaml_path, out_path):
#     try:
#         with open(yaml_path, 'r') as f:
#             config = yaml.safe_load(f)

#         duck_cfg = config['duckdb'][0]
#         DB_PATH = duck_cfg['DB_PATH']
#         DB_NAME = duck_cfg['DB_NAME']
#         TABLE_NAME = duck_cfg['TABLE_NAME']

#         full_db_path = os.path.join(DB_PATH, DB_NAME)

#         blocking_columns = config['blocking']['columns']
#         blocking_threshold = config['blocking'].get('threshold', [0.8])[0]  # Default threshold if not specified
#         similarity_configs = config['similarity']
        
#         # Handle thresholds with prompt if missing
#         if 'thresholds' not in config:
#             review_input = input("Enter review threshold (default 0.8): ") or "0.8"
#             auto_merge_input = input("Enter auto merge threshold (default 0.9): ") or "0.9"
#             thresholds = {
#                 'review': float(review_input),
#                 'auto_merge': float(auto_merge_input)
#             }
#         else:
#             thresholds = config['thresholds']
        
#         # Handle survivorship and priority_rule blocks with fallback logic
#         survivorship = config.get('survivorship', {})
#         survivorship_rules = survivorship.get('rules', [])
#         priority_rule = config.get('priority_rule', {})
#         priority_conditions = priority_rule.get('conditions', [])
        
#         # Check if both blocks are missing
#         has_survivorship = bool(survivorship_rules)
#         has_priority_rule = bool(priority_conditions)
        
#         if not has_survivorship and not has_priority_rule:
#             print("⚠️ Both 'survivorship' and 'priority_rule' blocks are missing. Please define at least one.")
#             # Continue with empty lists, but may lead to ties
        
#         # Print configuration status
#         if has_priority_rule and has_survivorship:
#             print("✅ Both priority_rule and survivorship blocks found - using priority_rule as primary, survivorship as fallback")
#         elif has_priority_rule and not has_survivorship:
#             print("⚠️ Only priority_rule block found - survivorship block missing, using priority_rule only")
#         elif not has_priority_rule and has_survivorship:
#             print("⚠️ Only survivorship block found - priority_rule block missing, using survivorship only")
#         else:
#             print("⚠️ No rules defined - will pick min record_id in case of ties")

#         # Handle unique_id columns
#         unique_id_cfg = config.get('unique_id', {})
#         unique_id_columns = unique_id_cfg.get('columns', [])
#         if not unique_id_columns:
#             response = input("Unique ID columns not provided. Enter comma-separated column names or press Enter to skip: ")
#             if response.strip():
#                 unique_id_columns = [c.strip() for c in response.split(',')]
#             else:
#                 unique_id_columns = []

#         con = duckdb.connect(database=full_db_path, read_only=False)

#         # Start timing for fuzzy blocking
#         blocking_start_time = time.time()

#         concat_expr = " || ' ' || ".join(f"CAST({c} AS VARCHAR)" for c in blocking_columns)
#         con.execute(f"""
#             CREATE OR REPLACE TEMP TABLE temp_blocking AS
#             SELECT row_number() OVER () AS record_id, *, ({concat_expr}) AS full_name
#             FROM {TABLE_NAME}
#         """)

#         con.execute(f"""
#             CREATE OR REPLACE TEMP TABLE candidate_pairs AS
#             SELECT a.record_id AS first, b.record_id AS second
#             FROM temp_blocking a
#             JOIN temp_blocking b ON a.record_id < b.record_id
#             WHERE jaro_winkler_similarity(a.full_name, b.full_name) > {blocking_threshold}
#         """)

#         blocking_end_time = time.time()
#         blocking_duration = blocking_end_time - blocking_start_time

#         # Compute pair similarities dynamically
#         sim_exprs = []
#         sum_sim_parts = []
#         n_sims = len(similarity_configs)
#         for sim_cfg in similarity_configs:
#             col = sim_cfg['column']
#             method = sim_cfg['method']
#             if method == 'jarowinkler':
#                 expr = f"jaro_winkler_similarity(a.{col}, b.{col}) AS sim_{col}"
#             elif method == 'exact':
#                 expr = f"(a.{col} = b.{col})::DOUBLE AS sim_{col}"
#             elif method == 'levenshtein':
#                 expr = f"1.0 - (levenshtein(a.{col}, b.{col}) / GREATEST(LENGTH(COALESCE(a.{col}, '')), LENGTH(COALESCE(b.{col}, '')))::DOUBLE) AS sim_{col}"
#             else:
#                 # Fallback to jaro_winkler for unsupported
#                 expr = f"jaro_winkler_similarity(a.{col}, b.{col}) AS sim_{col}"
#             sim_exprs.append(expr)
#             sum_sim_parts.append(f"sim_{col}")

#         sim_columns_sql = ', '.join(sim_exprs)
#         sum_sim = ' + '.join(sum_sim_parts)
#         overall_sim_expr = f"CASE WHEN {n_sims} > 0 THEN ({sum_sim}) / {n_sims} ELSE 0 END AS overall_sim"

#         pair_sim_query = f"""
#         CREATE OR REPLACE TEMP TABLE pair_similarities AS
#         SELECT p.first, p.second, {sim_columns_sql}, {overall_sim_expr}
#         FROM candidate_pairs p
#         JOIN temp_blocking a ON a.record_id = p.first
#         JOIN temp_blocking b ON b.record_id = p.second
#         """
#         con.execute(pair_sim_query)

#         review_threshold = thresholds['review']
#         auto_merge_threshold = thresholds['auto_merge']

#         # Create links tables
#         con.execute(f"""
#         CREATE OR REPLACE TEMP TABLE auto_merge_links AS
#         SELECT first, second
#         FROM pair_similarities
#         WHERE overall_sim >= {auto_merge_threshold}
#         """)

#         con.execute(f"""
#         CREATE OR REPLACE TEMP TABLE review_links AS
#         SELECT first, second, overall_sim
#         FROM pair_similarities
#         WHERE overall_sim >= {review_threshold} AND overall_sim < {auto_merge_threshold}
#         """)

#         # Create review_records
#         con.execute("""
#         CREATE OR REPLACE TEMP TABLE review_records AS
#         SELECT DISTINCT first AS record_id FROM review_links
#         UNION
#         SELECT DISTINCT second AS record_id FROM review_links
#         """)

#         has_clusters = con.execute("SELECT COUNT(*) FROM auto_merge_links").fetchone()[0] > 0

#         if has_clusters:
#             # Create edges, nodes, walks, components, cluster_members
#             con.execute("""
#             CREATE OR REPLACE TEMP TABLE edges AS
#             SELECT first AS src, second AS dst FROM auto_merge_links
#             UNION ALL
#             SELECT second AS src, first AS dst FROM auto_merge_links
#             """)

#             con.execute("""
#             CREATE OR REPLACE TEMP TABLE nodes AS
#             SELECT DISTINCT src AS node FROM edges
#             UNION
#             SELECT DISTINCT dst AS node FROM edges
#             """)

#             con.execute("""
#             CREATE OR REPLACE TEMP TABLE walks AS
#             WITH RECURSIVE walks(node, front) AS (
#                 SELECT node, node AS front
#                 FROM nodes
#                 UNION
#                 SELECT w.node, e.dst AS front
#                 FROM walks w
#                 JOIN edges e ON w.front = e.src
#             )
#             SELECT * FROM walks
#             """)

#             con.execute("""
#             CREATE OR REPLACE TEMP TABLE components AS
#             SELECT node, MIN(front) AS cluster_id
#             FROM walks
#             GROUP BY node
#             """)

#             con.execute("""
#             CREATE OR REPLACE TEMP TABLE cluster_members AS
#             SELECT c.cluster_id, t.record_id, t.*
#             FROM components c
#             JOIN temp_blocking t ON t.record_id = c.node
#             ORDER BY c.cluster_id, t.record_id
#             """)

#             # Conflicted includes review and cluster
#             con.execute("""
#             CREATE OR REPLACE TEMP TABLE conflicted_records AS
#             SELECT record_id FROM review_records
#             UNION
#             SELECT record_id FROM cluster_members
#             """)
#         else:
#             # No clusters, conflicted = review
#             con.execute("""
#             CREATE OR REPLACE TEMP TABLE conflicted_records AS
#             SELECT * FROM review_records
#             """)

#         # Single records
#         con.execute("""
#         CREATE OR REPLACE TEMP TABLE single_records_table AS
#         SELECT * FROM temp_blocking
#         WHERE record_id NOT IN (SELECT record_id FROM conflicted_records)
#         """)

#         # Function to pick survivor
#         def pick_survivor(group_df, priority_conds, surv_rules):
#             current = group_df.copy()
#             # Priority rules first
#             for cond in priority_conds:
#                 col = cond['column']
#                 val = cond['value']
#                 matches = current[current[col] == val]
#                 if not matches.empty:
#                     # Pick min record_id
#                     survivor = matches.loc[matches['record_id'].idxmin()]
#                     return survivor, f"priority | {col}"
#             # Survivorship rules
#             logic_parts = []
#             for rule in surv_rules:
#                 col = rule['column']
#                 strategy = rule['strategy']
#                 if strategy == 'most_recent':
#                     # Assume col is comparable, e.g., date string or datetime
#                     max_val = current[col].max()
#                     current = current[current[col] == max_val]
#                     logic_parts.append(f"{col} {strategy}")
#                 elif strategy == 'source_priority':
#                     source_order = rule.get('source_order', [])
#                     if source_order:
#                         prio_map = {src: i for i, src in enumerate(source_order)}
#                         current['prio'] = current[col].map(lambda x: prio_map.get(x, len(source_order) + 1))
#                         min_prio = current['prio'].min()
#                         current = current[current['prio'] == min_prio].drop('prio', axis=1)
#                         logic_parts.append(f"{col} {strategy}")
#                     else:
#                         continue  # Skip if no order
#                 elif strategy == 'longest_string':
#                     current['len_col'] = current[col].astype(str).str.len()
#                     max_len = current['len_col'].max()
#                     current = current[current['len_col'] == max_len].drop('len_col', axis=1)
#                     logic_parts.append(f"{col} {strategy}")
#                 if len(current) == 1:
#                     break
#             if len(current) == 1:
#                 survivor = current.iloc[0]
#                 logic_str = f"survivorship | {' | '.join(logic_parts)}" if logic_parts else "survivorship | none"
#                 return survivor, logic_str
#             else:
#                 # Tie, pick min record_id
#                 survivor = current.loc[current['record_id'].idxmin()]
#                 logic_str = f"survivorship | {' | '.join(logic_parts)} tie_min_id" if logic_parts else "tie_min_id"
#                 return survivor, logic_str

#         # Prepare golden records
#         golden_list = []

#         # Singles
#         single_query = """
#         SELECT record_id, * EXCLUDE (record_id, full_name) FROM single_records_table
#         """
#         single_df = con.execute(single_query).df()
#         for _, row in single_df.iterrows():
#             d = row.drop('record_id').to_dict()
#             d['Record_ID'] = row['record_id']
#             d['similar_record_ids'] = ''
#             d['logic'] = 'single'
#             if unique_id_columns:
#                 vals = [str(d.get(c, '')) for c in unique_id_columns]
#                 d['unique_id'] = hashlib.md5('|'.join(vals).encode('utf-8')).hexdigest()
#             else:
#                 d['unique_id'] = ''
#             golden_list.append(d)

#         # Merged from clusters
#         if has_clusters:
#             cluster_query = """
#             SELECT cluster_id, record_id, * EXCLUDE (record_id, full_name) FROM cluster_members
#             """
#             cluster_df = con.execute(cluster_query).df()
#             grouped = cluster_df.groupby('cluster_id')
#             for _, group in grouped:
#                 group_data = group.drop('cluster_id', axis=1)
#                 survivor_row, logic = pick_survivor(group_data, priority_conditions, survivorship_rules)
#                 d = survivor_row.drop('record_id').to_dict()
#                 d['Record_ID'] = survivor_row['record_id']
#                 similar_ids_list = sorted(group['record_id'].astype(str))
#                 d['similar_record_ids'] = '|'.join(similar_ids_list)
#                 d['logic'] = logic
#                 if unique_id_columns:
#                     vals = [str(d.get(c, '')) for c in unique_id_columns]
#                     d['unique_id'] = hashlib.md5('|'.join(vals).encode('utf-8')).hexdigest()
#                 else:
#                     d['unique_id'] = ''
#                 golden_list.append(d)

#         # Create golden_df and save
#         if golden_list:
#             golden_df = pd.DataFrame(golden_list)
#             # Register and create table
#             con.register('golden_temp', golden_df)
#             con.execute("DROP TABLE IF EXISTS golden_table")
#             con.execute("CREATE TABLE golden_table AS SELECT * FROM golden_temp")
#             # Export to CSV - ensure out_path is a proper filename
#             if os.path.isdir(out_path) or out_path == '.':
#                 # If out_path is a directory, create a filename
#                 timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                 csv_filename = f"golden_records_{timestamp}.csv"
#                 full_output_path = os.path.join(out_path, csv_filename)
#             else:
#                 # If out_path already includes filename, use it as is
#                 full_output_path = out_path
            
#             golden_df.to_csv(full_output_path, index=False)
#             print(f"✅ Golden records created: {len(golden_df)} records. Saved to 'golden_table' in DuckDB and '{full_output_path}'")
#         else:
#             print("⚠️ No golden records generated.")

#         # Print duration
#         print(f"Blocking took {blocking_duration:.2f} seconds")

#         con.close()
#         return True

#     except Exception as e:
#         print(f"❌ Error: {str(e)}")
#         if 'con' in locals():
#             con.close()
#         return False
