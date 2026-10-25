import os

import pytest

pytest.importorskip("airflow.models")

os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "false")

from airflow.models import DagBag  # type: ignore[import-not-found]


def test_no_import_errors():
    bag = DagBag(dag_folder="airflow/dags")
    assert bag.import_errors == {}


def test_dag_structure():
    bag = DagBag(dag_folder="airflow/dags")
    dag = bag.get_dag("ecommerce_etl")
    assert {t.task_id for t in dag.tasks} == {
        "ingest_orders", "dbt_build", "build_report"
    }
    assert dag.get_task("dbt_build").upstream_task_ids == {"ingest_orders"}
    assert dag.get_task("build_report").upstream_task_ids == {"dbt_build"}