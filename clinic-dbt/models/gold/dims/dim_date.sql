{{ config(materialized='table') }}

with dates as (
    select distinct
        to_date(appointment_date) as date_day
    from {{ ref('silver_appointments') }}
),

calendar as (
    select
        date_day,
        to_number(to_char(date_day, 'YYYYMMDD')) as date_key,
        year(date_day) as year,
        quarter(date_day) as quarter,
        month(date_day) as month,
        monthname(date_day) as month_name,
        dayofweekiso(date_day) as iso_day_of_week,
        dayname(date_day) as day_name
    from dates
)

select *
from calendar
