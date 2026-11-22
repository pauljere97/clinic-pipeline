{{ config(materialized='table') }}

select
    p.id as patient_id,
    p.user_id,
    u.first_name,
    u.last_name,
    u.email,
    u.city,
    u.gender,
    p.age,
    p.created_at
from {{ ref('silver_patients') }} p
left join {{ ref('silver_users') }} u
  on u.id = p.user_id
