select
    reading_id,
    meter_id,
    reading_timestamp,
    loaded_at,
    loaded_at - reading_timestamp as ingestion_latency

from {{ ref('stg_meter_readings') }}

where loaded_at > reading_timestamp + interval '1 hour'