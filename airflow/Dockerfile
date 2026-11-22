FROM apache/airflow:2.10.5-python3.12

USER airflow

COPY requirement.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

USER root
RUN apt-get update \
    && apt-get install --no-install-recommends -y git \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv /opt/dbt-venv \
    && /opt/dbt-venv/bin/pip install --no-cache-dir "dbt-core>=1.12,<2" "dbt-snowflake>=1.12,<2" \
    && ln -s /opt/dbt-venv/bin/dbt /usr/local/bin/dbt

COPY airflow/initialize.sh /opt/airflow/initialize.sh

USER airflow
