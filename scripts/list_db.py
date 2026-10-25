import sys

import duckdb

con = duckdb.connect(sys.argv[1], read_only=True)
rows = con.execute("""
    select table_schema || '.' || table_name as tbl, column_name, data_type
    from information_schema.columns
    where table_schema in ('raw', 'refined', 'reported')
    order by 1, ordinal_position
""").fetchall()
for r in rows:
    print(r)