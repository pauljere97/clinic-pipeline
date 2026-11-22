{{ config(materialized='table') }}

with latest_events as (
    select *
    from {{ ref('bronze_services') }}
    qualify row_number() over (
        partition by id
        order by coalesce(source_lsn, 0) desc,
                 coalesce(source_ts_ms, 0) desc,
                 cdc_id desc
    ) = 1
)

select
    id,
    trim(service_name) as service_name,
    cast(price as decimal(10, 2)) as price,
    cast(duration as integer) as duration,
    try_to_timestamp_ntz(created_at) as created_at,
    source_lsn,
    source_tx_id,
    source_timestamp,
    cdc_id,
    source_file,
    loaded_at
from latest_events
where operation != 'd'
  and id is not null
