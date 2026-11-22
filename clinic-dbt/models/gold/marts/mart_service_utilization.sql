{{ config(materialized='table') }}

select
    s.service_id,
    s.service_name,
    s.price,
    s.duration,
    count(*) as appointment_count,
    coalesce(sum(f.revenue), 0) as appointment_revenue
from {{ ref('fact_appointments') }} f
join {{ ref('dim_service') }} s
  on s.service_id = f.service_id
group by
    s.service_id,
    s.service_name,
    s.price,
    s.duration
