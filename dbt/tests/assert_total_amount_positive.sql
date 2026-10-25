select order_id, quantity, unit_price, discount, total_amount
from {{ ref('refined_orders') }}
where quantity <= 0 or unit_price < 0 or total_amount < 0