import os
import requests
import duckdb
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import time

load_dotenv()

# --- CONFIGURATION ---
TECHNOLOGIES = [
    "python", "java", "javascript", "csharp", "c++", "go", "rust",
    "php", "r", "c", "visual basic", "delphi", "fortran", "ada",
    "perl", "matlab", "assembly", "cobol",
]
DB_FILE = 'dbt_project/raw_data.db'
GITHUB_TOKEN = os.getenv("GITHUB_PAT")

def get_github_data(tech_list):
    if not GITHUB_TOKEN:
        raise ValueError("GitHub PAT not found. Make sure it's set in your .env file.")

    print("Fetching GitHub data... (This will take a long time due to API rate limits)")
    all_repo_data = []
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    today = datetime.now()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - pd.Timedelta(days=1)
    
    end_year = last_day_of_previous_month.year
    end_month = last_day_of_previous_month.month

    print(f"--> Fetching historical data from Jan 2018 up to the end of {end_year}-{end_month:02d}.")

    for year in range(2018, end_year + 1):
        last_month_in_year = end_month if year == end_year else 12
        for month in range(1, last_month_in_year + 1):
            start_date_str = f"{year}-{month:02d}-01"
            end_of_month = pd.Period(f'{year}-{month}').days_in_month
            end_date_str = f"{year}-{month:02d}-{end_of_month}"
            
            for tech in tech_list:
                print(f"  - Fetching for '{tech}' in {year}-{month:02d}")
                query = f'language:"{tech}" created:{start_date_str}..{end_date_str}'
                url = f"https://api.github.com/search/repositories?q={query}"
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    count = response.json().get("total_count", 0)
                    all_repo_data.append({
                        "language": tech, "repo_count": count,
                        "month_year": f"{year}-{month:02d}-01"
                    })
                    print("    > Pausing for 1s...")
                    time.sleep(1) 
                except requests.exceptions.RequestException as e:
                    print(f"    ! Error fetching data for '{tech}' ({year}-{month}): {e}")
                    time.sleep(30)
                    continue
    return pd.DataFrame(all_repo_data)

def load_to_duckdb(df, table_name, db_file):
    print(f"\nLoading data into DuckDB table '{table_name}'...")
    con = duckdb.connect(db_file)
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
    print(f"✅ Successfully loaded {len(df)} rows into '{db_file}'")
    con.close()

if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    github_df = get_github_data(TECHNOLOGIES)
    if not github_df.empty:
        load_to_duckdb(github_df, 'raw_github', DB_FILE)
    else:
        print("No GitHub data was fetched. The database was not updated.")
    print("\nETL process finished.")