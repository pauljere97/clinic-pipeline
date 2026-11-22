#!/bin/sh
set -eu

case "${AWS_S3_BUCKET_ARN:?Set AWS_S3_BUCKET_ARN in .env}" in
    arn:aws:s3:::*)
        bucket_name=${AWS_S3_BUCKET_ARN#arn:aws:s3:::}
        ;;
    *)
        printf '%s\n' "AWS_S3_BUCKET_ARN must be a standard S3 bucket ARN (arn:aws:s3:::bucket-name)." >&2
        exit 1
        ;;
esac

case "$bucket_name" in
    ''|*[!a-z0-9.-]*)
        printf '%s\n' "The S3 bucket ARN does not contain a valid bucket name." >&2
        exit 1
        ;;
esac

attempt=0
until curl -fsS "${CONNECT_URL:?}/connectors" >/dev/null; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 60 ]; then
        printf '%s\n' "Kafka Connect did not become ready within 120 seconds." >&2
        exit 1
    fi
    sleep 2
done

wait_for_connector() {
    name=$1
    attempt=0
    while [ "$attempt" -lt 60 ]; do
        status=$(curl -fsS "$CONNECT_URL/connectors/$name/status")
        case "$status" in
            *'"state":"FAILED"'*)
                printf 'Connector %s failed; inspect Kafka Connect logs for details.\n' "$name" >&2
                return 1
                ;;
        esac
        if printf '%s' "$status" | grep -Eq '"connector":\{"state":"RUNNING".*"tasks":\[.*"state":"RUNNING"'; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    printf 'Connector %s did not become healthy within 120 seconds.\n' "$name" >&2
    return 1
}

curl -fsS -X PUT \
    -H "Content-Type: application/json" \
    --data-binary @/config/postgres-source.json \
    "$CONNECT_URL/connectors/clinic-postgres/config"

sed "s/__S3_BUCKET_NAME__/$bucket_name/g" /config/s3-sink.json \
    | curl -fsS -X PUT \
        -H "Content-Type: application/json" \
        --data-binary @- \
        "$CONNECT_URL/connectors/clinic-s3-sink/config"

wait_for_connector clinic-postgres
wait_for_connector clinic-s3-sink

printf '\nRegistered the PostgreSQL source and S3 sink connectors.\n'
