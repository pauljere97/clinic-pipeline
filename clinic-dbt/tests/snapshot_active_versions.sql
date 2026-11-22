with all_active_versions as (
    select 'users' as snapshot_name, id, dbt_valid_to
    from {{ ref('snap_users') }}
    union all
    select 'patients' as snapshot_name, id, dbt_valid_to
    from {{ ref('snap_patients') }}
    union all
    select 'doctors' as snapshot_name, id, dbt_valid_to
    from {{ ref('snap_doctors') }}
    union all
    select 'services' as snapshot_name, id, dbt_valid_to
    from {{ ref('snap_services') }}
    union all
    select 'appointments' as snapshot_name, id, dbt_valid_to
    from {{ ref('snap_appointments') }}
)

select snapshot_name, id
from all_active_versions
where dbt_valid_to is null
group by snapshot_name, id
having count(*) != 1
