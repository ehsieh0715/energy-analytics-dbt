select
    meter_id,
    reading_date,
    count(*) as row_count

from {{ ref('int_daily_consumption') }}

group by
    meter_id,
    reading_date

having count(*) > 1