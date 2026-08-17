select
    meter_id,
    customer_id,
    meter_type,
    installation_date,
    meter_status

from {{ ref('stg_meters') }}