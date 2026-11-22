from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor


DEFAULT_ARGS = {
    "owner": "clinic-pipeline",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}

with DAG(
    dag_id="load_silver_models",
    description="Build Snowflake silver current-state models after bronze succeeds",
    start_date=datetime(2024, 1, 1),
    schedule=timedelta(minutes=10),
    catchup=False,
    max_active_runs=1,
    default_args=DEFAULT_ARGS,
    tags=["clinic-pipeline", "silver", "snowflake", "dbt"],
) as dag:
    wait_for_bronze = ExternalTaskSensor(
        task_id="wait_for_bronze_models",
        external_dag_id="load_bronze_models",
        external_task_id="build_bronze_models",
        allowed_states=["success"],
        failed_states=["failed", "upstream_failed"],
        mode="reschedule",
        poke_interval=60,
        timeout=timedelta(minutes=20).total_seconds(),
    )

    build_silver = BashOperator(
        task_id="build_silver_models",
        bash_command=(
            "dbt build "
            "--select path:models/silver "
            "--project-dir /opt/airflow/clinic-dbt "
            "--profiles-dir /opt/airflow/.dbt"
        ),
    )

    wait_for_bronze >> build_silver
