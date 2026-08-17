select
    meter_id,
    customer_id,
    {{ normalize_text('meter_type') }} as meter_type,
    cast(installation_date as date) as installation_date,
    {{ normalize_text('meter_status') }} as meter_status

from {{ source('raw', 'meters') }}