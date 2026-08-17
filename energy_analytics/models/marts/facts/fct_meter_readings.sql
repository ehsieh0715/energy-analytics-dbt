{{
    config(
        materialized='incremental',
        unique_key='reading_id'
    )
}}

select
    reading_id,
    meter_id,
    reading_timestamp,
    consumption_kwh,
    reading_type

from {{ ref('stg_meter_readings') }}

{% if is_incremental() %}

where reading_timestamp > (
    select max(reading_timestamp) - interval '2 days'
    from {{ this }}
)

{% endif %}