{% macro bronze_relation() -%}
    {{ target.database }}.bronze
{%- endmacro %}

{% macro bronze_setup() %}
    {% set bucket_arn = env_var('AWS_S3_BUCKET_ARN', '') %}
    {% set role_arn = env_var('SNOWFLAKE_AWS_ROLE_ARN', '') %}

    {% if bucket_arn == '' %}
        {{ exceptions.raise_compiler_error(
            "AWS_S3_BUCKET_ARN is required. Set it to arn:aws:s3:::<bucket-name>."
        ) }}
    {% endif %}

    {% if role_arn == '' %}
        {{ exceptions.raise_compiler_error(
            "SNOWFLAKE_AWS_ROLE_ARN is required to create the Snowflake S3 storage integration."
        ) }}
    {% endif %}

    {% if not bucket_arn.startswith('arn:aws:s3:::') %}
        {{ exceptions.raise_compiler_error(
            "AWS_S3_BUCKET_ARN must use the form arn:aws:s3:::<bucket-name>."
        ) }}
    {% endif %}

    {% set bucket_name = bucket_arn.replace('arn:aws:s3:::', '') %}

    {% do run_query("create schema if not exists " ~ target.database ~ ".bronze") %}
    {% do run_query(
        "create or replace file format " ~ target.database ~
        ".bronze.clinic_json_gzip type = json compression = gzip"
    ) %}
    {% do run_query(
        "create storage integration if not exists clinic_s3_bronze "
        ~ "type = external_stage storage_provider = s3 enabled = true "
        ~ "storage_aws_role_arn = '" ~ role_arn ~ "' "
        ~ "storage_allowed_locations = ('s3://" ~ bucket_name ~ "/clinic/raw/')"
    ) %}
    {% do run_query(
        "create or replace stage " ~ target.database ~ ".bronze.clinic_cdc_s3 "
        ~ "url = 's3://" ~ bucket_name ~ "/clinic/raw/' "
        ~ "storage_integration = clinic_s3_bronze "
        ~ "file_format = " ~ target.database ~ ".bronze.clinic_json_gzip"
    ) %}

    {% set integration_details = run_query(
        "desc integration clinic_s3_bronze"
    ) %}
    {{ log("Snowflake storage integration created.", info=True) }}
    {% for row in integration_details.rows %}
        {{ log(row, info=True) }}
    {% endfor %}
{% endmacro %}

{% macro bronze_load_cdc_events() %}
    {% set bucket_arn = env_var('AWS_S3_BUCKET_ARN', '') %}
    {% if bucket_arn == '' %}
        {{ exceptions.raise_compiler_error("AWS_S3_BUCKET_ARN is required.") }}
    {% endif %}

    create schema if not exists {{ target.database }}.bronze;

    create file format if not exists {{ target.database }}.bronze.clinic_json_gzip
        type = json
        compression = gzip;

    create table if not exists {{ target.database }}.bronze.bronze_cdc_events (
        raw_record variant,
        source_file varchar,
        file_row_number number,
        loaded_at timestamp_ltz,
        cdc_id varchar
    );

    copy into {{ target.database }}.bronze.bronze_cdc_events
        (raw_record, source_file, file_row_number, loaded_at, cdc_id)
    from (
        select
            $1,
            metadata$filename,
            metadata$file_row_number,
            current_timestamp(),
            metadata$filename || ':' || metadata$file_row_number
        from @{{ target.database }}.bronze.clinic_cdc_s3
    )
    file_format = (format_name = '{{ target.database }}.bronze.clinic_json_gzip')
    pattern = '.*[.]json[.]gz'
    on_error = 'abort_statement';
{% endmacro %}

{% macro bronze_s3_list() %}
    {% set result = run_query(
        "list @" ~ target.database ~ ".bronze.clinic_cdc_s3"
    ) %}
    {% for row in result.rows %}
        {{ log(row, info=True) }}
    {% endfor %}
{% endmacro %}
