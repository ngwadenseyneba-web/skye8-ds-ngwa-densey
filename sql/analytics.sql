-- What percentage of harvests met the target in each season?

SELECT
    season,
    COUNT(*) AS total_harvests,
    COUNT(*) FILTER (WHERE met_target = TRUE) AS targets_met,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE met_target = TRUE)
        / NULLIF(COUNT(*), 0),
        2
    ) AS target_attainment_pct
FROM harvests
GROUP BY season
ORDER BY season;

-- What is the mean yield for each crop within each division,
-- and how does each crop's mean compare with the division mean?

WITH crop_division_yield AS (
    SELECT
        f.division,
        p.crop,
        AVG(h.yield_kg_ha) AS mean_crop_yield
    FROM farms f
    JOIN plots p
        ON f.farm_id = p.farm_id
    JOIN harvests h
        ON p.plot_id = h.plot_id
    GROUP BY
        f.division,
        p.crop
)
SELECT
    division,
    crop,
    ROUND(mean_crop_yield, 2) AS mean_crop_yield,
    ROUND(
        AVG(mean_crop_yield) OVER (
            PARTITION BY division
        ),
        2
    ) AS division_mean_yield
FROM crop_division_yield
ORDER BY
    division,
    mean_crop_yield DESC;


-- Which three plots have the highest yield for each crop?

WITH ranked_plots AS (
    SELECT
        p.crop,
        p.plot_id,
        f.division,
        h.season,
        h.yield_kg_ha,
        RANK() OVER (
            PARTITION BY p.crop
            ORDER BY h.yield_kg_ha DESC
        ) AS yield_rank
    FROM plots p
    JOIN farms f
        ON p.farm_id = f.farm_id
    JOIN harvests h
        ON p.plot_id = h.plot_id
)
SELECT
    crop,
    plot_id,
    division,
    season,
    yield_kg_ha,
    yield_rank
FROM ranked_plots
WHERE yield_rank <= 3
ORDER BY
    crop,
    yield_rank;

-- How does target attainment change from one season to the next?

WITH seasonal_attainment AS (
    SELECT
        season,
        AVG(
            CASE
                WHEN met_target = TRUE THEN 1.0
                ELSE 0.0
            END
        ) * 100 AS attainment_pct
    FROM harvests
    GROUP BY season
)
SELECT
    season,
    ROUND(attainment_pct, 2) AS attainment_pct,
    ROUND(
        attainment_pct
        - LAG(attainment_pct) OVER (
            ORDER BY season
        ),
        2
    ) AS change_from_previous_season
FROM seasonal_attainment
ORDER BY season;


-- Find divisions whose average yield is above the overall
-- average yield.

SELECT
    f.division,
    AVG(h.yield_kg_ha) AS average_yield
FROM farms f
JOIN plots p
    ON f.farm_id = p.farm_id
JOIN harvests h
    ON p.plot_id = h.plot_id
GROUP BY f.division
HAVING AVG(h.yield_kg_ha) > (
    SELECT AVG(yield_kg_ha)
    FROM harvests
)
ORDER BY average_yield DESC;

-- Same analysis rewritten using CTEs

WITH overall_yield AS (
    SELECT
        AVG(yield_kg_ha) AS overall_average_yield
    FROM harvests
),
division_yields AS (
    SELECT
        f.division,
        AVG(h.yield_kg_ha) AS average_yield
    FROM farms f
    JOIN plots p
        ON f.farm_id = p.farm_id
    JOIN harvests h
        ON p.plot_id = h.plot_id
    GROUP BY f.division
)
SELECT
    d.division,
    d.average_yield
FROM division_yields d
CROSS JOIN overall_yield o
WHERE d.average_yield > o.overall_average_yield
ORDER BY d.average_yield DESC;


 -- PERFORMANCE ANALYSIS
 -- EXPLAIN ANALYZE BEFORE INDEX

EXPLAIN ANALYZE
SELECT
    f.division,
    p.crop,
    AVG(h.yield_kg_ha) AS average_yield
FROM farms f
JOIN plots p
    ON f.farm_id = p.farm_id
JOIN harvests h
    ON p.plot_id = h.plot_id
GROUP BY
    f.division,
    p.crop;

-- Index used to support joins between plots and harvests.

CREATE INDEX IF NOT EXISTS idx_harvests_plot_id
ON harvests(plot_id);

-- EXPLAIN ANALYZE After INDEX

EXPLAIN ANALYZE
SELECT
    f.division,
    p.crop,
    AVG(h.yield_kg_ha) AS average_yield
FROM farms f
JOIN plots p
    ON f.farm_id = p.farm_id
JOIN harvests h
    ON p.plot_id = h.plot_id
GROUP BY
    f.division,
    p.crop;



