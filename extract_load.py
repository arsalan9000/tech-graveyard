import os
import requests
import duckdb
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# This line loads the GITHUB_PAT from your .env file
load_dotenv()

# --- CONFIGURATION ---
# Feel free to change this list to track different technologies.
# Use the lowercase name/tag that is common on GitHub/Stack Overflow.
TECHNOLOGIES = [
    "angularjs", "react", "vue.js", "svelte", 
    "jquery", "ember.js", "backbone.js", "knockout.js"
]

# The database file will be created inside your dbt project directory
DB_FILE = 'dbt_project/raw_data.db'

# Your GitHub Personal Access Token is read from the environment
GITHUB_TOKEN = os.getenv("GITHUB_PAT")

# --- FUNCTIONS ---

def get_github_data(tech_list):
    """
    Fetches monthly new repository counts from the GitHub API for a list of technologies.
    It iterates from 2018 to the current month.
    """
    if not GITHUB_TOKEN:
        raise ValueError("GitHub PAT not found. Make sure it's set in your .env file.")

    print("Fetching GitHub data... (This may take a few minutes)")
    all_repo_data = []
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Define the time range for data collection
    for year in range(2018, datetime.now().year + 1):
        for month in range(1, 13):
            # Stop if we are in a future month of the current year
            if year == datetime.now().year and month > datetime.now().month:
                break

            start_date = f"{year}-{month:02d}-01"
            # Get the last day of the month
            end_of_month = pd.Period(f'{year}-{month}').days_in_month
            end_date = f"{year}-{month:02d}-{end_of_month}"
            
            for tech in tech_list:
                print(f"  - Fetching for '{tech}' in {year}-{month:02d}")
                
                # Construct the search query for the GitHub API
                query = f'"{tech}" created:{start_date}..{end_date}'
                url = f"https://api.github.com/search/repositories?q={query}"
                
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status() # Raises an exception for 4XX/5XX errors
                    
                    count = response.json().get("total_count", 0)
                    
                    all_repo_data.append({
                        "language": tech,
                        "repo_count": count,
                        "month_year": f"{year}-{month:02d}-01" # Store as first day of the month
                    })
                except requests.exceptions.RequestException as e:
                    print(f"    ! Error fetching data for '{tech}' ({year}-{month}): {e}")
                    # This often happens if you hit the API rate limit.
                    # The script will continue with the next item.
                    continue

    return pd.DataFrame(all_repo_data)


def load_to_duckdb(df, table_name, db_file):
    """
    Loads a pandas DataFrame into a specified table in a DuckDB database.
    It will create the table or replace it if it already exists.
    """
    print(f"\nLoading data into DuckDB table '{table_name}'...")
    con = duckdb.connect(db_file)
    # The 'CREATE OR REPLACE TABLE' command is idempotent, which is perfect for our pipeline
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
    print(f"✅ Successfully loaded {len(df)} rows into '{db_file}'")
    con.close()


# --- MAIN EXECUTION ---

if __name__ == "__main__":
    # Ensure the directory for the database exists before trying to create the file
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    
    # Run the extraction and loading process
    github_df = get_github_data(TECHNOLOGIES)
    
    if not github_df.empty:
        load_to_duckdb(github_df, 'raw_github', DB_FILE)
    else:
        print("No GitHub data was fetched. The database was not updated.")

    print("\nETL process finished.")