select
    customer_id,
    meter_id,
    reading_date,
    total_consumption_kwh,
    reading_count

from {{ ref('int_customer_daily_consumption') }}