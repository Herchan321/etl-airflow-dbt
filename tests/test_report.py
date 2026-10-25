import duckdb
from reporting.build_report import build_report


def test_build_report(tmp_path):
    db = str(tmp_path / "t.duckdb")
    con = duckdb.connect(db)
    con.execute("create schema reported")
    con.execute("""
        create table reported.sales as
        select 1 as order_id, date '2026-10-01' as order_date,
               'Pomme' as product_name, 'Food' as category,
               2 as quantity, 10.0 as total_amount
        union all
        select 2, date '2026-10-02', 'Poire', 'Food', 1, 5.0
    """)
    con.close()

    out = tmp_path / "report.html"
    build_report(db, str(out))

    html = out.read_text(encoding="utf-8")
    assert "Rapport ventes" in html
    assert "15.00" in html      # chiffre d'affaires
    assert "Pomme" in html