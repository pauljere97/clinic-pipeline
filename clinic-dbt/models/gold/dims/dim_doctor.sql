{{ config(materialized='table') }}

select
    d.id as doctor_id,
    d.user_id,
    u.first_name,
    u.last_name,
    u.email,
    u.city,
    u.gender,
    d.specialization,
    d.created_at
from {{ ref('silver_doctors') }} d
left join {{ ref('silver_users') }} u
  on u.id = d.user_id
