import duckdb

con = duckdb.connect(r"init_db\ecommerce.duckdb", read_only=True)

print("--- raw (échantillon) ---")
print(con.execute("""
    select order_id, order_date, quantity, unit_price, discount, shipping_cost
    from raw.orders limit 8
""").df().to_string())

print("\n--- valeurs de discount ---")
print(con.execute("""
    select discount, count(*) n from raw.orders
    group by 1 order by 2 desc limit 10
""").df().to_string())

print("\n--- ancien refined (ta logique d'origine) ---")
print(con.execute("""
    select order_id, order_date, quantity, unit_price, discount,
           shipping_cost, total_amount
    from refined.orders limit 8
""").df().to_string())

print("\n--- lignes ---")
print(con.execute("""
    select (select count(*) from raw.orders) as raw_rows,
           (select count(*) from refined.orders) as refined_rows
""").df().to_string())