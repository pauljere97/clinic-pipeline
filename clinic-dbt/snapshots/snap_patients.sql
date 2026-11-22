{% snapshot snap_patients %}

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
from {{ ref('silver_patients') }}

{% endsnapshot %}
