# 💀 The Tech Graveyard: A Data-Driven Monitor of Fading Technologies

This is an end-to-end data engineering project that automatically tracks the adoption trends of various programming languages on GitHub. It ingests data via the GitHub REST API, processes it using a modern data stack, and serves an interactive dashboard that visualizes which technologies are rising in popularity and which are fading away.

The entire pipeline is automated using GitHub Actions to ensure the data is always fresh, and the dashboard is deployed live using Streamlit Community Cloud.

**[➡️ View the Live Dashboard Here](https://tech-graveyard.streamlit.app/)** 

---

## 📊 Dashboard Preview


<img src="https://ibb.co/qMTfrHh7" alt="Dashboard Screenshot"/>

---

## ⚙️ Tech Stack & Architecture

This project is built using a modern, scalable, and zero-cost data stack, emphasizing current best practices in data engineering.

*   **Orchestration:** `GitHub Actions` for scheduled, serverless execution of the data pipeline.
*   **Data Ingestion:** `Python` (`requests`) to extract historical data from the GitHub REST API.
*   **Data Warehouse:** `DuckDB` for a lightweight, file-based, and high-performance analytical engine.
*   **Data Transformation:** `dbt` (Data Build Tool) to clean, model, and transform raw API data into analytics-ready tables.
*   **Data App / Dashboard:** `Streamlit` for building and serving the interactive web application.
*   **Deployment:** `Streamlit Community Cloud` for free, continuous deployment directly from the GitHub repository.

### Architecture Diagram

The project follows a modern ELT (Extract, Load, Transform) paradigm.

```
+---------------------+      +-------------------------------------------------------------+
|   GitHub REST API   |----->|                     GitHub Actions Workflow                   |
+---------------------+      |                  (Scheduled to run weekly)                    |
                             |                                                             |
                             |   [1. extract_load.py] -> [2. dbt run] -> [3. git commit]    |
                             +--------------------------------+------------------------------+
                                                              | (Pushes updated .db file)
                                                              v
+-------------------------------------------------------------+------------------------------+
|                        GitHub Repository                      |   Streamlit Community Cloud    |
|                                                             |                              |
|   [ app.py, dbt_project/, raw_data.db ] <-------------------> |  (Reads repo files to serve   |
|                                                             |   the live application)        |
+-------------------------------------------------------------+------------------------------+
```

---

## 🚀 How to Run Locally

To clone this project and run it on your own machine, please follow these steps.

### Prerequisites
*   Python 3.9+
*   Git
*   A GitHub account

### 1. Clone the Repository
Open your terminal and run the following commands:
```bash
git clone https://github.com/YOUR_USERNAME/tech-graveyard.git
cd tech-graveyard
```

### 2. Set Up a Virtual Environment
It is a strong best practice to use a virtual environment to manage project-specific dependencies.

```bash
# Create the virtual environment
python -m venv .venv

# Activate the environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
Install all the required Python packages from the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

### 4. Set Up API Credentials
This project requires a GitHub Personal Access Token (PAT) to access the API and avoid strict rate limits.

1.  [Generate a new PAT on GitHub](https://github.com/settings/tokens/new).
2.  Select **"Tokens (classic)"**.
3.  Give it a descriptive name (e.g., "TechGraveyard Project") and grant it the **`public_repo`** scope.
4.  Copy the generated token.
5.  Create a new file named `.env` in the root of the project directory.
6.  Add your token to the `.env` file in the following format:
    ```
    GITHUB_PAT=ghp_YourTokenStringHere...
    ```
    *(The `.gitignore` file is already configured to prevent this file from being committed.)*

### 5. Run the Data Pipeline
This is a two-step process to first fetch the raw data and then transform it for analysis.

```bash
# 1. Fetch data from the GitHub API.
# WARNING: This script is intentionally slow to respect API rate limits
# and will take approximately 1 hour to complete.
python extract_load.py

# 2. Run dbt to transform the raw data into our final analytics table.
cd dbt_project
dbt run --profiles-dir .
cd ..
```

### 6. Launch the Streamlit App
Once the pipeline has finished, you can start the web application.
```bash
streamlit run app.py
```
Your web browser should automatically open with the dashboard running locally at `http://localhost:8501`.

---

## 🤖 Automation with GitHub Actions

This repository contains a GitHub Actions workflow defined in `.github/workflows/daily_data_refresh.yml`. This workflow automates the entire data pipeline (`extract_load.py` and `dbt run`) and runs on a schedule (e.g., weekly).

After successfully running, the action commits the updated `raw_data.db` file back to the repository. The live Streamlit application automatically uses this new data, ensuring the dashboard is always up-to-date without any manual intervention.

---

## 🔮 Future Enhancements

*   **Integrate Additional Data Sources:** Incorporate data from the Stack Overflow API or job boards like Hacker News to create a more holistic "Technology Interest Index".
*   **Implement Data Quality Tests:** Add `dbt-expectations` or `Soda Core` to the pipeline to automatically test for data freshness, duplicates, or anomalies.
*   **Advanced Trend Analysis:** Use more sophisticated statistical models to detect trend inflection points or forecast future adoption rates.
