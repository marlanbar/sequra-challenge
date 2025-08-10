-- Query to find the maximum number of times a core has been reused
SELECT core, MAX(reuse_count) AS max_reuse_count
FROM (
    SELECT core, COUNT(*) - 1 AS reuse_count
    FROM spacex_launches
    GROUP BY core
) AS core_reuse_counts;