# clinic_dbt

This dbt project loads PostgreSQL CDC data from S3 into Snowflake bronze
models and creates current-state silver tables.

The local profile is stored in the repository's ignored `.dbt/profiles.yml`.
Replace its `private_key_path` placeholder with the absolute path to the
Snowflake private key file. Keep the key file outside this repository.

From the repository root, activate the project environment once per terminal:

```sh
source .venv/bin/activate
```

Then run dbt commands from the repository root:

```sh
dbt debug --project-dir clinic-dbt --profiles-dir .dbt
dbt parse --project-dir clinic-dbt --profiles-dir .dbt
```
