{% snapshot snap_services %}

{{
    config(
        target_schema='snapshot',
        unique_key='id',
        strategy='check',
        check_cols='all',
        invalidate_hard_deletes=true
    )
}}

select *
from {{ ref('silver_services') }}

{% endsnapshot %}
