{{
    config(
        materialized='incremental',
        incremental_strategy='append',
        pre_hook="{{ bronze_load_cdc_events() }}"
    )
}}

select *
from {{ this }}
where 1 = 0
