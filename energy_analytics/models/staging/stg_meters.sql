select
    meter_id,
    customer_id,
    meter_type,
    cast(installation_date as date) as installation_date,
    lower(meter_status) as meter_status

from {{ source('raw', 'meters') }}