{{ config(alias='orders') }}

with typed as (
    select
        try_cast(order_id as integer)                         as order_id,
        try_strptime(order_date, '%m/%d/%Y')::date            as order_date,
        try_cast(customer_id as integer)                      as customer_id,
        trim(customer_name)                                   as customer_name,
        lower(trim(customer_email))                           as customer_email,
        trim(country)                                         as country,
        trim(city)                                            as city,
        try_cast(product_id as integer)                       as product_id,
        trim(product_name)                                    as product_name,
        trim(category)                                        as category,
        try_cast(quantity as integer)                         as quantity,
        try_cast(unit_price as decimal(10,2))                 as unit_price,
        coalesce(try_cast(discount as decimal(10,2)), 0)      as discount,
        coalesce(try_cast(shipping_cost as decimal(10,2)), 0) as shipping_cost,
        trim(payment_method)                                  as payment_method
    from {{ source('raw', 'orders') }}
)

select
    *,
    cast(quantity * unit_price - discount + shipping_cost as decimal(12,2))
        as total_amount
from typed
where order_id is not null
qualify row_number() over (partition by order_id order by order_date, customer_id) = 1