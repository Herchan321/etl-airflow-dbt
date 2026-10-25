import os
from datetime import datetime

import duckdb

DB_PATH = os.getenv("DUCKDB_PATH", "/opt/airflow/data/ecommerce.duckdb")
OUT = os.getenv("REPORT_PATH", "/opt/airflow/reports/report.html")


def build_report(db_path: str = DB_PATH, out: str = OUT) -> str:
    con = duckdb.connect(db_path, read_only=True)
    try:
        kpi = con.execute("""
            select sum(total_amount), count(*), sum(total_amount) / count(*)
            from reported.sales
        """).fetchone()
        daily = con.execute("""
            select order_date, count(*) as nb_orders,
                   sum(total_amount) as revenue
            from reported.sales group by 1 order by 1
        """).df()
        top = con.execute("""
            select product_name, category, sum(quantity) as units,
                   sum(total_amount) as revenue
            from reported.sales group by 1, 2
            order by revenue desc limit 10
        """).df()
    finally:
        con.close()

    html = f"""<html><head><meta charset="utf-8"><title>Rapport ventes</title></head>
<body style="font-family:sans-serif;max-width:900px;margin:auto">
<h1>Rapport ventes</h1><p>Généré le {datetime.now():%Y-%m-%d %H:%M}</p>
<h2>KPIs</h2>
<ul><li>Chiffre d'affaires : {kpi[0]:,.2f}</li>
<li>Commandes : {kpi[1]:,}</li>
<li>Panier moyen : {kpi[2]:,.2f}</li></ul>
<h2>Top 10 produits</h2>{top.to_html(index=False)}
<h2>Ventes par jour</h2>{daily.to_html(index=False)}
</body></html>"""
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out