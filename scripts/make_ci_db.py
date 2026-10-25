import os

import duckdb

con = duckdb.connect(os.environ["DUCKDB_PATH"])
con.execute("create schema if not exists raw")
con.execute("""
    create or replace table raw.orders as
    select '1' as order_id, '10/1/2026' as order_date, '5' as customer_id,
           'A B' as customer_name, 'A@x.com' as customer_email,
           'MA' as country, 'Rabat' as city, '7' as product_id,
           'Pomme' as product_name, 'Food' as category, '2' as quantity,
           '10.00' as unit_price, '1.00' as discount,
           '2.00' as shipping_cost, 'card' as payment_method
    union all
    -- doublon volontaire (meme order_id) : le dedoublonnage doit le retirer
    select '1', '10/1/2026', '5', 'A B', 'A@x.com', 'MA', 'Rabat',
           '7', 'Pomme', 'Food', '2', '10.00', '1.00', '2.00', 'card'
    union all
    select '2', '10/2/2026', '6', 'C D', 'c@x.com', 'MA', 'Fes',
           '8', 'Poire', 'Food', '1', '5.00', '0.00', '1.00', 'cash'
""")
con.close()
print("ci db ready")