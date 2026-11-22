{{ config(materialized='table') }}

select
    id as user_id,
    first_name,
    last_name,
    email,
    city,
    gender,
    created_at
from {{ ref('silver_users') }}
