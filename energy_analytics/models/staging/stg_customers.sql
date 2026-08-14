select
    customer_id,
    customer_name,
    email,
    city,
    signup_date,
    customer_status

from {{ source('raw', 'customers') }}