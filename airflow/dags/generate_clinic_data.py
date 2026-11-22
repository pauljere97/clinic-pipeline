from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="generate_clinic_data",
    description="Create sample clinic data in PostgreSQL",
    start_date=datetime(2024, 1, 1),
    schedule="0 0 * * *", # Run every day at 1 AM
    catchup=False,
    tags=["clinic-pipeline", "postgres"],
) as dag:
    BashOperator(
        task_id="generate_clinic_data",
        bash_command="python /opt/airflow/postgres/data_generation.py",
    )
