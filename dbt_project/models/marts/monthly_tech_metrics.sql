with source_data as (
    select * from {{ ref('stg_github_data') }}
)

select
    language,
    metric_date,
    repo_count,

    -- Calculate the percentage change from the previous month for the same language
    (repo_count - lag(repo_count, 1, repo_count) over (partition by language order by metric_date)) * 100.0 /
    nullif(lag(repo_count, 1, repo_count) over (partition by language order by metric_date), 0) as percent_change_from_previous_month

from source_data
order by language, metric_date