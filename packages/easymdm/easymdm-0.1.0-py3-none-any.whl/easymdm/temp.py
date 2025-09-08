import duckdb
import yaml
import os

# def load_duckdb_data(schema_table, yaml_path):
def load_duckdb_data(yaml_path):

    try:
        # Load DB config from YAML file
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)

        # Extract DuckDB config
        duck_cfg = config['duckdb'][0]
        DB_PATH = duck_cfg['DB_PATH']
        DB_NAME = duck_cfg['DB_NAME']
        TABLE_NAME = duck_cfg['TABLE_NAME']

        full_db_path = os.path.join(DB_PATH, DB_NAME)

        # Extract blocking columns
        blocking_columns = config['blocking']['columns']
        if len(blocking_columns) < 2:
            raise ValueError("At least two columns are required for similarity comparison.")

        # Connect to DuckDB
        con = duckdb.connect(database=full_db_path, read_only=False)

        # Construct SQL expression to concatenate columns
        concat_expr = " || ' ' || ".join(blocking_columns)
        alias_expr = f"({concat_expr}) AS full_name"

        # Create a temporary view with concatenated names
        con.execute(f"""
            CREATE OR REPLACE TEMP VIEW temp_blocking AS
            SELECT *, {alias_expr}
            FROM {TABLE_NAME}
        """)

        # Perform Jaro-Winkler similarity search using DuckDB's `similarity` function
        # Compare each row with every other row (self join)
        # result = con.execute(f"""
        #     SELECT 
        #         a.full_name AS name1,
        #         b.full_name AS name2,
        #         similarity(a.full_name, b.full_name, 'jarowinkler') AS jw_score
        #     FROM temp_blocking a
        #     JOIN temp_blocking b
        #     ON a.full_name != b.full_name
        #     WHERE similarity(a.full_name, b.full_name, 'jarowinkler') > 0.85
        #     ORDER BY jw_score DESC
        # """).fetchall()
        
        # Export to CSV before closing connection
        output_csv_path = os.path.join(DB_PATH, 'temp_blocking_output.csv')
        con.execute(f"""
            COPY temp_blocking TO '{output_csv_path}' (HEADER, DELIMITER ',');
        """)

        print(f"✅ View exported to CSV at: {output_csv_path}")
        
        # Close connection
        con.close()

        # return result

    except Exception as e:
        print(f"Error: {e}")
        # return []

# Example usage:
# matches = load_duckdb_data('my_schema.my_table', 'config.yaml')
# for match in matches:
#     print(match)

if __name__ == '__main__':
    # matches = load_duckdb_data('my_schema.my_table', r'D:\mygit\easymdm-1\sample\testdata.yaml')
    matches = load_duckdb_data(r'D:\mygit\easymdm-1\sample\testdata.yaml')

    # for match in matches:
    #     print(match)
