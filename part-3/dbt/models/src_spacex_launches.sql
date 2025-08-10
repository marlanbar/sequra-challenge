-- models/src_spacex_launches.sql
WITH raw_data AS (
    SELECT
        id,
        name,
        date_utc,
        core,
        payload,
        launchpad,
        success
    FROM {{ source('spacex', 'launches') }}
)

SELECT * FROM raw_data