select
    dbt_scd_id as customer_version_id,
    customer_id,
    customer_name,
    email,
    city,
    customer_status,
    dbt_valid_from as valid_from,
    dbt_valid_to as valid_to,

    case
        when dbt_valid_to is null then true
        else false
    end as is_current

from {{ ref('customer_snapshot') }}