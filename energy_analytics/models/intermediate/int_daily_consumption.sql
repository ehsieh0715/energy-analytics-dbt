select
    meter_id,
    cast(reading_timestamp as date) as reading_date,
    sum(consumption_kwh) as total_consumption_kwh,
    count(*) as reading_count

from {{ ref('stg_meter_readings') }}

group by
    meter_id,
    cast(reading_timestamp as date)