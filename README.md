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