select
    reading_id,
    meter_id,
    cast(reading_timestamp as timestamp) as reading_timestamp,
    cast(consumption_kwh as decimal(10, 2)) as consumption_kwh,
    {{ normalize_text('reading_type') }} as reading_type

from {{ source('raw', 'meter_readings') }}