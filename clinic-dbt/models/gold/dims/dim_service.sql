{{ config(materialized='table') }}

select
    id as service_id,
    service_name,
    price,
    duration,
    created_at
from {{ ref('silver_services') }}
