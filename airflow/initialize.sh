#!/usr/bin/env bash
set -euo pipefail

airflow db migrate

existing_users="$(airflow users list --output json)"
if ! printf '%s' "$existing_users" | python -c \
    'import json, sys; sys.exit(0 if any(user["username"] == sys.argv[1] for user in json.load(sys.stdin)) else 1)' \
    "$AIRFLOW_ADMIN_USERNAME"; then
    airflow users create \
        --username "$AIRFLOW_ADMIN_USERNAME" \
        --password "$AIRFLOW_ADMIN_PASSWORD" \
        --firstname Airflow \
        --lastname Admin \
        --role Admin \
        --email "$AIRFLOW_ADMIN_USERNAME@example.com"
fi
