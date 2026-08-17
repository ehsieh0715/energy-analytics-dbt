select
    customer_id,
    count(*) as current_version_count

from {{ ref('dim_customer_history') }}

where is_current = true

group by customer_id

having count(*) != 1