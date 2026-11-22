{{
    config(materialized='incremental', incremental_strategy='append', unique_key='cdc_id')
}}

with cdc as (
    select *
    from {{ ref('bronze_cdc_events') }}
    where raw_record:source:schema::varchar = 'public'
      and raw_record:source:table::varchar = 'services'
),
flattened as (
    select
        cdc_id,
        raw_record:op::varchar as operation,
        raw_record:source:lsn::number as source_lsn,
        raw_record:source:txId::number as source_tx_id,
        raw_record:ts_ms::number as source_ts_ms,
        to_timestamp_ntz(raw_record:ts_ms::number / 1000) as source_timestamp,
        coalesce(raw_record:after, raw_record:before):id::number as id,
        coalesce(raw_record:after, raw_record:before):service_name::varchar as service_name,
        coalesce(raw_record:after, raw_record:before):price::number as price,
        coalesce(raw_record:after, raw_record:before):duration::number as duration,
        coalesce(raw_record:after, raw_record:before):created_at::varchar as created_at,
        raw_record:before as before_row,
        raw_record:after as after_row,
        source_file,
        file_row_number,
        loaded_at
    from cdc
)

select *
from flattened
{% if is_incremental() %}
where cdc_id not in (select cdc_id from {{ this }})
{% endif %}
