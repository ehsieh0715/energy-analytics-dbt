with customers as (

    select *
    from {{ ref('stg_customers') }}

),

meters as (

    select *
    from {{ ref('stg_meters') }}

),

daily_consumption as (

    select *
    from {{ ref('int_daily_consumption') }}

)

select
    customers.customer_id,
    customers.customer_name,
    customers.city,
    meters.meter_id,
    meters.meter_type,
    daily_consumption.reading_date,
    daily_consumption.total_consumption_kwh,
    daily_consumption.reading_count

from daily_consumption

inner join meters
    on daily_consumption.meter_id = meters.meter_id

inner join customers
    on meters.customer_id = customers.customer_id