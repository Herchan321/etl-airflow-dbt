{{ config(alias='sales') }}

select
    order_id, order_date, customer_id, country, city,
    product_id, product_name, category, quantity,
    unit_price, discount, shipping_cost, total_amount, payment_method
from {{ ref('refined_orders') }}s