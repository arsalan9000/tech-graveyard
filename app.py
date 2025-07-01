import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
# This should be the first Streamlit command.
st.set_page_config(
    page_title="The Tech Graveyard",
    page_icon="💀",
    layout="wide",
)

# --- Database Connection & Data Loading ---
# Using st.cache_data is crucial for performance. It prevents re-running
# the query every time the user interacts with a widget.
@st.cache_data
def get_data_from_db():
    """Connects to DuckDB and fetches the final, transformed data."""
    try:
        con = duckdb.connect('dbt_project/raw_data.db', read_only=True)
        # Query the final 'mart' table created by dbt
        df = con.execute("SELECT * FROM monthly_tech_metrics").fetchdf()
        con.close()
        # Ensure the date column is in datetime format for Plotly
        df['metric_date'] = pd.to_datetime(df['metric_date'])
        return df
    except duckdb.IOException:
        # Return an empty DataFrame if the DB file doesn't exist
        return pd.DataFrame()

# Load the data at the start of the script
df = get_data_from_db()

# --- Page Title and Introduction ---
st.title("💀 The Tech Graveyard")
st.markdown("""
A data-driven look at which programming languages and frameworks are fading in popularity.
This dashboard tracks the number of **new public repositories** created on GitHub each month,
a key indicator of new project adoption and developer interest.
""")

# --- Main Application Logic ---
# First, check if the dataframe is empty (which means the pipeline hasn't run)
if df.empty:
    st.error("Data not found. Please run the data pipeline first by following the steps in the README.md file.")
else:
    # --- Sidebar for User Controls ---
    st.sidebar.header("Dashboard Filters")
    
    # Get a sorted, unique list of technologies for the multiselect widget
    all_techs = sorted(df["language"].unique())
    
    selected_techs = st.sidebar.multiselect(
        "Select technologies to compare:",
        options=all_techs,
        # Set a sensible default to show some data on first load
        default=all_techs[:4] 
    )

    # Check if the user has selected any technologies
    if not selected_techs:
        st.warning("Please select at least one technology from the sidebar to display the charts.")
    else:
        # Filter the main dataframe based on the user's selection
        filtered_df = df[df["language"].isin(selected_techs)].copy()

        # --- Time Series Chart ---
        st.header("Monthly New Repositories Over Time")
        fig_time_series = px.line(
            filtered_df,
            x="metric_date",
            y="repo_count",
            color="language",
            title="Trend of New Public Repositories on GitHub",
            labels={"metric_date": "Date", "repo_count": "Number of New Repositories", "language": "Technology"},
            hover_name="language",
            hover_data={"metric_date": "|%B %Y", "repo_count": True}
        )
        fig_time_series.update_layout(legend_title_text='Technology')
        st.plotly_chart(fig_time_series, use_container_width=True)

        # --- Analysis of Recent Trends (in columns) ---
        st.header("Analysis of Recent Trends")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Latest Month's Activity")
            # Find the most recent month in the filtered data to display
            latest_month = filtered_df["metric_date"].max()
            latest_data = filtered_df[filtered_df["metric_date"] == latest_month]
            
            fig_latest_bar = px.bar(
                latest_data.sort_values("repo_count", ascending=False),
                x="language",
                y="repo_count",
                color="language",
                title=f"New Repos in {latest_month.strftime('%B %Y')}",
                labels={"repo_count": "Number of New Repos", "language": "Technology"}
            )
            fig_latest_bar.update_layout(showlegend=False) # Hide legend as colors are obvious
            st.plotly_chart(fig_latest_bar, use_container_width=True)

        with col2:
            st.subheader("Monthly Growth/Decline (%)")
            # Use the same 'latest_data' dataframe for the table
            latest_growth_data = latest_data[["language", "percent_change_from_previous_month"]].set_index("language")
            
            # Format the percentage for better readability
            latest_growth_data['percent_change_from_previous_month'] = latest_growth_data['percent_change_from_previous_month'].apply(
                lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A"
            )
            st.dataframe(latest_growth_data, use_container_width=True)
            st.caption("This table shows the percentage change in new repositories in the latest month compared to the prior month.")

        # --- Raw Data Expander ---
        with st.expander("View Filtered Raw Data"):
            # Show the raw data, sorted for readability
            st.dataframe(filtered_df.sort_values(["language", "metric_date"], ascending=[True, False]), use_container_width=True)