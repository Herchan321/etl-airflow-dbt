from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from include.ingest_orders import run as ingest_run

from reporting.build_report import build_report

with DAG(
    "ecommerce_etl",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=2)},
) as dag:
    ingest = PythonOperator(task_id="ingest_orders", python_callable=ingest_run)
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="cd /opt/airflow/dbt && /home/airflow/dbt_venv/bin/dbt build --profiles-dir .",
    )
    report = PythonOperator(task_id="build_report", python_callable=build_report)
    ingest >> dbt_build >> report
    