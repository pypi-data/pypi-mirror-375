import duckdb
import os
import yaml

def upload_csv_to_duckdb(csv_path, db_folder, db_name, table_name):
    try:
        # Construct full path to DuckDB database
        db_path = os.path.join(db_folder, db_name)

        # Connect to DuckDB
        con = duckdb.connect(database=db_path, read_only=False)

        # Load CSV into DuckDB (auto-detects schema)
        con.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT * FROM read_csv_auto('{csv_path}', HEADER=True)
        """)

        print(f"✅ CSV data uploaded to DuckDB table '{table_name}' at: {db_path}")
        con.close()

    except Exception as e:
        print(f"❌ Error: {e}")

def upload_duckdb_main(file_name,config_path):
    try:
        # Load DB config from YAML file
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Access first item in the 'sqlite' list
        duckdb_cfg = config['duckdb'][0]
        DB_PATH = duckdb_cfg['DB_PATH']
        DB_NAME = duckdb_cfg['DB_NAME']
        TABLE_NAME = duckdb_cfg['TABLE_NAME']

        upload_csv_to_duckdb(file_name, DB_PATH, DB_NAME, TABLE_NAME)

    except ValueError:
        raise ValueError("Table must be in 'duck db' format.")
    except Exception as e:
        raise ValueError(f"Error loading duckdb data: {str(e)}")

# # Example usage
# csv_file = r'D:\mygit\easymdm-1\sample\mock17k.csv' # mock30k testdata
# duckdb_folder = r'D:\mygit\easymdm-1\sample\\'
# duckdb_name = 'mock.duckdb'#'mock.duckdb' 'text.duckdb'
# table_name =  'mock17k'#'mock30k'
