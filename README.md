# Clinic pipeline

## Run the sample data DAG

1. Copy `env.example` to `.env` and set the PostgreSQL settings and the
   `AIRFLOW_DB_*` and `AIRFLOW_ADMIN_*` credentials. Use URL-safe characters
   for `AIRFLOW_DB_PASSWORD`. Generate a shared webserver signing key with
   `python -c "import secrets; print(secrets.token_urlsafe(32))"` and set
   `AIRFLOW_WEBSERVER_SECRET_KEY` to its output.
2. Start PostgreSQL and Airflow:

   ```sh
   docker compose up --build
   ```

3. Open [http://localhost:8080](http://localhost:8080) and log in with the
   `AIRFLOW_ADMIN_USERNAME` and `AIRFLOW_ADMIN_PASSWORD` values from `.env`.
4. Unpause and trigger the `generate_clinic_data` DAG. Its task creates the
   clinic tables and inserts sample users, patients, doctors, services, and
   appointments into PostgreSQL.

The DAG is manually triggered and can be run again to generate additional
sample records.

All Airflow components use the same `AIRFLOW_WEBSERVER_SECRET_KEY`; keep it
stable across restarts. After adding or changing it, recreate the Airflow
services with `docker compose up -d --force-recreate airflow-init airflow-webserver airflow-scheduler`.

## Stream PostgreSQL changes to S3

The local CDC stack uses Kafka, Kafka Connect, Debezium, and the Confluent S3
Sink connector. It snapshots all tables in the PostgreSQL `public` schema and
then streams ongoing inserts, updates, and deletes. This includes the
Faker-generated `users.password` values; use only synthetic data.

1. In `.env`, set `AWS_S3_BUCKET_ARN` to the ARN of an existing private S3
   bucket, provide AWS credentials with permission to locate the bucket and
   write objects, and set `AWS_REGION` (the example defaults to `eu-north-1`).
   Do not commit `.env`. Enable the bucket's default encryption.
2. Start the stack:

   ```sh
   docker compose up --build -d
   ```

3. Trigger `generate_clinic_data` in Airflow so the tables exist before
   Debezium creates its publication and takes the initial snapshot.
4. Register the connectors:

   ```sh
   docker compose --profile cdc-init run --rm connect-init
   ```

5. Check connector status:

   ```sh
   curl -fsS http://localhost:8083/connectors/clinic-postgres/status
   curl -fsS http://localhost:8083/connectors/clinic-s3-sink/status
   ```

The sink writes compressed JSON CDC records below `clinic/raw/`, grouped by
topic and Kafka partition. It flushes at 100 records or on a one-minute UTC
schedule. Debezium's delete event is retained; Kafka tombstone records are
ignored. Since delivery is at-least-once, downstream consumers should dedupe
using the record key and source LSN.

## Load S3 CDC files into Snowflake bronze models

Set `SNOWFLAKE_AWS_ROLE_ARN` in `.env` to the IAM role that Snowflake should
use for the S3 storage integration. The role must allow
`s3:GetObject`, `s3:GetObjectVersion`, and `s3:ListBucket` for
`clinic-pipeline-1` and the `clinic/raw/` prefix. Then create the Snowflake
storage objects once:

```sh
set -a
. .env
set +a
source .venv/bin/activate
dbt run-operation bronze_setup \
  --project-dir clinic-dbt \
  --profiles-dir .dbt
```

`bronze_setup` prints no credentials and creates `CLINIC.BRONZE`,
`clinic_s3_bronze`, `CLINIC.BRONZE.CLINIC_CDC_S3`, and the gzip JSON file
format. Snowflake will return an AWS IAM user ARN and external ID for the
storage integration when it is created; add those values to the IAM role trust
policy before loading data.

Run the bronze models:

```sh
dbt build --select path:models/bronze \
  --project-dir clinic-dbt \
  --profiles-dir .dbt
```

## Run bronze models periodically in Airflow

Set `SNOWFLAKE_PRIVATE_KEY_PATH` in `.env` to the absolute private-key file
path outside this repository. Docker Compose mounts that file at the same
container path and mounts the dbt project and profile directory into Airflow.

The `load_bronze_models` DAG runs every 10 minutes with one active run, retries
twice, and executes:

```sh
dbt build --select path:models/bronze \
  --project-dir /opt/airflow/clinic-dbt \
  --profiles-dir /opt/airflow/.dbt
```

The `load_silver_models` DAG runs on the same 10-minute schedule and waits for
the bronze DAG's matching bronze build to succeed. It then builds the silver
current-state models. The silver layer contains deduplicated users, patients,
doctors, services, and appointments. It applies deletes and removes passwords
from the current-state user table.

The `load_snapshots` DAG runs every 10 minutes, waits for the matching silver
build to succeed, and executes `dbt snapshot`. It snapshots users, patients,
doctors, services, and appointments in `CLINIC.SNAPSHOT`, recording changed
versions and invalidating rows removed from the silver tables.

Rebuild and recreate Airflow after changing the Compose mounts:

```sh
docker compose up -d --build --force-recreate \
  airflow-init airflow-webserver airflow-scheduler
```

The bronze layer is intentionally append-oriented:

- `bronze_cdc_events` stores the complete raw Debezium envelope.
- The topic models flatten CDC events for users, patients, doctors, services,
  and appointments.
- `cdc_id` combines the S3 filename and file row number to deduplicate
  at-least-once deliveries.
- Delete events retain the record's `before` row and set `after_row` to null.

The source connector currently uses the local PostgreSQL `POSTGRES_USER`
credentials, which are typically superuser credentials in this development
Compose setup. Before using real data or a production database, replace these
with a dedicated replication account with only the required replication and
table-read permissions. The Compose Kafka and Connect listeners are intended
for local development, not direct production exposure.