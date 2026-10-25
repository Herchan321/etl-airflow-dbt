FROM apache/airflow:3.3.2

# dbt dans un venv séparé : évite les conflits de dépendances avec Airflow
RUN python -m venv /home/airflow/dbt_venv \
 && /home/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-duckdb duckdb==1.5.6

# ingestion (PythonOperator) dans l'environnement d'Airflow
RUN pip install --no-cache-dir duckdb==1.5.6 requests pandas