"""
Load FHIR JSON data into DuckDB database
creates raw tables from generated synthetic FHIR data 
"""


import json
import duckdb
from pathlib import Path

def load_json_to_table (conn, json_file: Path, table_name: str):
    """ Load JSON file into duckdb table."""
    with open(json_file, 'r') as f:
        data = json.load(f)

    if not data:
        print (f"Caution: {json_file.name} is empty")
        return
    #To Convert list of dicts to duckDB table
    conn.execute(f"Create or REplace Table raw_{table_name} AS Select * From read_json_auto('{json_file}')")
    count = conn.execute(f"Select Count(*) From raw_{table_name}").fetchone()[0]
    print (f"Loaded  {count} rows into raw_{table_name}")


def main():
    """Load all FHIR daat into duckDB."""
    # To Craete data directory if it does not exist
    db_path = Path ("data/ehr_analytics.duckdb")
    raw_data_dir = Path("data/raw")
    print("Connecting to DuckDB..")
    conn = duckdb.connect(str(db_path))

    #To load each JSON filr
    file_to_load ={
        'patients': raw_data_dir / 'patients.json',
        'conditions': raw_data_dir / 'conditions.json',
        'medications': raw_data_dir / 'medications.json',
        'observations': raw_data_dir / 'observations.json',
        'clinical_notes': raw_data_dir / 'clinical_notes.json'
    }
    print("\nLoading data into DuckDB..")
    for table_name, json_file in file_to_load.items():
        load_json_to_table(conn, json_file, table_name)

    #To show sumamry
    print("\n" + "="*50)
    print("Database Summary".center(50))
    print("="*50)

    tables = conn.execute("Show Tables").fetchall()
    for table in tables:
        table_name = table [0]
        row_count = conn.execute(f"Select Count(*) From {table_name}").fetchone()[0]
        print(f"{table_name}:{row_count} rows")

    print(f"\n Database SAVED  to: {db_path}")
    conn.close()

if __name__ == "__main__":
    main()
    