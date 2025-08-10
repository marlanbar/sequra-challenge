-- models/spacex_launches.sql

{{ config(
    materialized='incremental',
    unique_key='id'
) }}

WITH spacex_launches AS (
    SELECT
        id,
        name,
        CAST(date_utc AS TIMESTAMP) AS launch_date,
        core,
        payload,
        launchpad,
        success
    FROM {{ ref('spacex_launches') }}
)

SELECT * FROM spacex_launches

{% if is_incremental() %}
  WHERE launch_date > (SELECT MAX(launch_date) FROM {{ this }})
{% endif %}