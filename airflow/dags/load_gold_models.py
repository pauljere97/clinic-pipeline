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
    dag_id="load_gold_models",
    description="Build Snowflake gold dimensions, facts, and marts",
    start_date=datetime(2024, 1, 1),
    schedule=timedelta(minutes=10),
    catchup=False,
    max_active_runs=1,
    default_args=DEFAULT_ARGS,
    tags=["clinic-pipeline", "gold", "snowflake", "dbt"],
) as dag:
    wait_for_snapshots = ExternalTaskSensor(
        task_id="wait_for_snapshots",
        external_dag_id="load_snapshots",
        external_task_id="build_snapshots",
        allowed_states=["success"],
        failed_states=["failed", "upstream_failed"],
        mode="reschedule",
        poke_interval=60,
        timeout=timedelta(minutes=20).total_seconds(),
    )

    build_gold = BashOperator(
        task_id="build_gold_models",
        bash_command=(
            "dbt build "
            "--select path:models/gold "
            "--project-dir /opt/airflow/clinic-dbt "
            "--profiles-dir /opt/airflow/.dbt"
        ),
    )

    wait_for_snapshots >> build_gold
