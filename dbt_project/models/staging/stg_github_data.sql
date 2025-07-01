select
    language,
    repo_count,
    cast(month_year as date) as metric_date
from {{ source('raw_data', 'raw_github') }}