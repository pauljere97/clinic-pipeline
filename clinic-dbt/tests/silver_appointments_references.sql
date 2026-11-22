select appointment_id
from (
    select
        a.id as appointment_id,
        p.id as patient_id,
        d.id as doctor_id,
        s.id as service_id
    from {{ ref('silver_appointments') }} as a
    left join {{ ref('silver_patients') }} as p on p.id = a.patient_id
    left join {{ ref('silver_doctors') }} as d on d.id = a.doctor_id
    left join {{ ref('silver_services') }} as s on s.id = a.service_id
)
where patient_id is null
   or doctor_id is null
   or service_id is null
