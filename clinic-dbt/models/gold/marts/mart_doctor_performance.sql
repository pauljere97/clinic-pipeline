{{ config(materialized='table') }}

select
    d.doctor_id,
    d.first_name,
    d.last_name,
    d.specialization,
    count(*) as appointment_count,
    coalesce(sum(f.revenue), 0) as appointment_revenue,
    coalesce(avg(f.duration), 0) as average_duration_minutes
from {{ ref('fact_appointments') }} f
join {{ ref('dim_doctor') }} d
  on d.doctor_id = f.doctor_id
group by
    d.doctor_id,
    d.first_name,
    d.last_name,
    d.specialization
