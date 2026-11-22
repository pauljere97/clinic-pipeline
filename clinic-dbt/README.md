# clinic_dbt

This dbt project is scaffolded to validate the Snowflake connection. No clinic
data models or loading steps are included yet.

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

Do not run `dbt run` or `dbt build` during initialization; those commands can
create objects in Snowflake once models are added.
