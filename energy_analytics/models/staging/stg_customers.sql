select
    customer_id,
    customer_name,
    email,
    city,
    signup_date,
    {{ normalize_text('customer_status') }} as customer_status

from {{ source('raw', 'customers') }}