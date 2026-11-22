from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


DEFAULT_ARGS = {
    "owner": "clinic-pipeline",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}

with DAG(
    dag_id="load_bronze_models",
    description="Load new S3 CDC files into Snowflake bronze models",
    start_date=datetime(2024, 1, 1),
    schedule="0 0 * * *", # Run every day at 1 AM
    catchup=False,
    max_active_runs=1,
    default_args=DEFAULT_ARGS,
    tags=["clinic-pipeline", "bronze", "snowflake", "dbt"],
) as dag:
    BashOperator(
        task_id="build_bronze_models",
        bash_command=(
            "dbt build "
            "--select path:models/bronze "
            "--project-dir /opt/airflow/clinic-dbt "
            "--profiles-dir /opt/airflow/.dbt"
        ),
    )
