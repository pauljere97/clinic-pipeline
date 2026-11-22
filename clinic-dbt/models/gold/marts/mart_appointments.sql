{{ config(materialized='table') }}

select
    f.appointment_id,
    f.appointment_date,
    f.date_key,
    f.patient_id,
    p.first_name as patient_first_name,
    p.last_name as patient_last_name,
    f.doctor_id,
    d.first_name as doctor_first_name,
    d.last_name as doctor_last_name,
    d.specialization,
    f.service_id,
    s.service_name,
    f.price,
    f.duration,
    f.revenue
from {{ ref('fact_appointments') }} f
left join {{ ref('dim_patient') }} p
  on p.patient_id = f.patient_id
left join {{ ref('dim_doctor') }} d
  on d.doctor_id = f.doctor_id
left join {{ ref('dim_service') }} s
  on s.service_id = f.service_id
