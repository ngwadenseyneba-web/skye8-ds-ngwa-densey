


-- Display all farms.

SELECT *
FROM farms;



-- Display farms from the division "Bui".

SELECT *
FROM farms
WHERE division = 'Bui';



-- Find farms with altitude above 1000 m and household size
-- greater than 5.

SELECT *
FROM farms
WHERE altitude_m > 1000
  AND household_size > 5;



-- Display plots from largest to smallest area.

SELECT *
FROM plots
ORDER BY area_ha DESC;




-- Display the 10 plots with the largest areas.

SELECT *
FROM plots
ORDER BY area_ha DESC
LIMIT 10;



-- Count the total number of farms, plots and harvests.

SELECT COUNT(*) AS total_farms
FROM farms;

SELECT COUNT(*) AS total_plots
FROM plots;

SELECT COUNT(*) AS total_harvests
FROM harvests;



-- Calculate the minimum, maximum and average yield.

SELECT
    MIN(yield_kg_ha) AS minimum_yield,
    MAX(yield_kg_ha) AS maximum_yield,
    AVG(yield_kg_ha) AS average_yield
FROM harvests;



-- Count the number of plots for each crop.

SELECT
    crop,
    COUNT(*) AS plot_count
FROM plots
GROUP BY crop
ORDER BY plot_count DESC;



-- Find crops that have more than 100 plots.

SELECT
    crop,
    COUNT(*) AS plot_count
FROM plots
GROUP BY crop
HAVING COUNT(*) > 100
ORDER BY plot_count DESC;



-- Calculate average area and average slope for each crop.

SELECT
    crop,
    COUNT(*) AS number_of_plots,
    AVG(area_ha) AS average_area_ha,
    AVG(slope_pct) AS average_slope_pct
FROM plots
GROUP BY crop
ORDER BY average_area_ha DESC;



-- Display each plot together with its farm's village and division.

SELECT
    p.plot_id,
    p.farm_id,
    p.crop,
    p.area_ha,
    f.village,
    f.division
FROM plots p
INNER JOIN farms f
    ON p.farm_id = f.farm_id;



-- Display all farms and their plots.
-- Farms without plots should also appear.

SELECT
    f.farm_id,
    f.village,
    f.division,
    p.plot_id,
    p.crop
FROM farms f
LEFT JOIN plots p
    ON f.farm_id = p.farm_id
ORDER BY f.farm_id;



-- Display all plots and their corresponding farms.
-- This demonstrates a RIGHT JOIN.

SELECT
    f.farm_id,
    f.village,
    f.division,
    p.plot_id,
    p.crop
FROM farms f
RIGHT JOIN plots p
    ON f.farm_id = p.farm_id;



-- Display all farms and all plots, including unmatched records.

SELECT
    f.farm_id,
    f.village,
    p.plot_id,
    p.crop
FROM farms f
FULL OUTER JOIN plots p
    ON f.farm_id = p.farm_id;



-- Combine farms, plots and harvests.

SELECT
    f.farm_id,
    f.village,
    f.division,
    p.plot_id,
    p.crop,
    h.harvest_id,
    h.season,
    h.yield_kg_ha,
    h.met_target
FROM farms f
INNER JOIN plots p
    ON f.farm_id = p.farm_id
INNER JOIN harvests h
    ON p.plot_id = h.plot_id;



-- Find harvests whose yield is greater than the overall
-- average yield.

SELECT
    harvest_id,
    plot_id,
    season,
    yield_kg_ha
FROM harvests
WHERE yield_kg_ha > (
    SELECT AVG(yield_kg_ha)
    FROM harvests
)
ORDER BY yield_kg_ha DESC;



-- Find harvests whose yield is greater than the average yield
-- for their own season.

SELECT
    h.harvest_id,
    h.season,
    h.yield_kg_ha
FROM harvests h
WHERE h.yield_kg_ha > (
    SELECT AVG(h2.yield_kg_ha)
    FROM harvests h2
    WHERE h2.season = h.season
)
ORDER BY h.season, h.yield_kg_ha DESC;



-- Classify harvests into yield categories.

SELECT
    harvest_id,
    yield_kg_ha,
    CASE
        WHEN yield_kg_ha < 1000 THEN 'Low'
        WHEN yield_kg_ha < 2000 THEN 'Medium'
        ELSE 'High'
    END AS yield_category
FROM harvests
ORDER BY yield_kg_ha;



-- Compare COUNT(*) with COUNT(fertiliser_kg_ha) and calculate
-- the average fertiliser application.

SELECT
    COUNT(*) AS total_harvests,
    COUNT(fertiliser_kg_ha) AS non_null_fertiliser_records,
    COUNT(*) - COUNT(fertiliser_kg_ha) AS missing_fertiliser_records,
    AVG(fertiliser_kg_ha) AS average_fertiliser
FROM harvests;



-- Calculate average yield by division.

SELECT
    f.division,
    COUNT(h.harvest_id) AS harvest_count,
    AVG(h.yield_kg_ha) AS average_yield
FROM farms f
INNER JOIN plots p
    ON f.farm_id = p.farm_id
INNER JOIN harvests h
    ON p.plot_id = h.plot_id
GROUP BY f.division
ORDER BY average_yield DESC;


-- Find divisions whose average yield is above the overall
-- average yield.

WITH division_yields AS (
    SELECT
        f.division,
        AVG(h.yield_kg_ha) AS average_yield
    FROM farms f
    INNER JOIN plots p
        ON f.farm_id = p.farm_id
    INNER JOIN harvests h
        ON p.plot_id = h.plot_id
    GROUP BY f.division
)
SELECT
    division,
    average_yield
FROM division_yields
WHERE average_yield > (
    SELECT AVG(yield_kg_ha)
    FROM harvests
)
ORDER BY average_yield DESC;


-- Create one list containing all villages and divisions.

SELECT village AS location
FROM farms

UNION

SELECT division AS location
FROM farms

ORDER BY location;



-- Find values that appear both as a village and as a division.

SELECT village AS location
FROM farms

INTERSECT

SELECT division AS location
FROM farms

ORDER BY location;


-- Find villages that do not also appear as divisions.

SELECT village AS location
FROM farms

EXCEPT

SELECT division AS location
FROM farms

ORDER BY location;



-- Rank harvests by yield within each season.

SELECT
    harvest_id,
    season,
    yield_kg_ha,
    RANK() OVER (
        PARTITION BY season
        ORDER BY yield_kg_ha DESC
    ) AS yield_rank
FROM harvests
ORDER BY season, yield_rank;