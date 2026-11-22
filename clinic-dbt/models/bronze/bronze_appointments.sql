{{
    config(materialized='incremental', incremental_strategy='append', unique_key='cdc_id')
}}

WITH cdc AS (
    SELECT *
    FROM {{ ref('bronze_cdc_events') }}
    WHERE raw_record:source:schema::varchar = 'public'
      AND raw_record:source:table::varchar = 'appointments'
),
flattened AS (
    SELECT
        cdc_id,
        raw_record:op::varchar as operation,
        raw_record:source:lsn::number as source_lsn,
        raw_record:source:txId::number as source_tx_id,
        raw_record:ts_ms::number as source_ts_ms,
        to_timestamp_ntz(raw_record:ts_ms::number / 1000) as source_timestamp,
        coalesce(raw_record:after, raw_record:before):id::number as id,
        coalesce(raw_record:after, raw_record:before):patient_id::number as patient_id,
        coalesce(raw_record:after, raw_record:before):doctor_id::number as doctor_id,
        coalesce(raw_record:after, raw_record:before):service_id::number as service_id,
        coalesce(raw_record:after, raw_record:before):appointment_date::varchar as appointment_date,
        coalesce(raw_record:after, raw_record:before):created_at::varchar as created_at,
        raw_record:before as before_row,
        raw_record:after as after_row,
        source_file,
        file_row_number,
        loaded_at
    FROM cdc
)

SELECT *
FROM flattened
{% if is_incremental() %}
WHERE cdc_id NOT IN (SELECT cdc_id FROM {{ this }})
{% endif %}
