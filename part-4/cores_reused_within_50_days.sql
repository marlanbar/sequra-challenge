-- Query to find the cores that have been reused in less than 50 days after the previous launch
WITH spacex_launches_days_between AS (
    SELECT 
        core,
        launch_date                                                                                         AS current_launch_date,
        LAG(launch_date) OVER (PARTITION BY core ORDER BY launch_date)                                      AS previous_launch_date,
        DATEDIFF(day, LAG(launch_date) OVER (PARTITION BY core ORDER BY launch_date), launch_date)          AS days_between
    FROM spacex_launches
)

SELECT 
    core,
    current_launch_date,
    previous_launch_date,
    days_between
FROM spacex_launches_days_between
WHERE days_between < 50;