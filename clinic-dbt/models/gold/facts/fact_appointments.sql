{{ config(materialized='table') }}

select
    a.id as appointment_id,
    to_number(to_char(to_date(a.appointment_date), 'YYYYMMDD')) as date_key,
    a.patient_id,
    a.doctor_id,
    a.service_id,
    a.appointment_date,
    a.created_at,
    s.price,
    s.duration,
    s.price as revenue
from {{ ref('silver_appointments') }} a
left join {{ ref('silver_services') }} s
  on s.id = a.service_id
