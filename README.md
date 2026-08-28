# Skye8 Data Science / ML Internship

## Project 1 — How Models Lie

This repository contains my implementation of Skye8 Project Brief 1.

The project demonstrates how incorrect machine-learning evaluation can produce misleadingly high performance estimates and develops an evaluation protocol to prevent these problems.

## Project Stages

- Stage A — Engineering Environment
- Stage B — Database
- Stage C — SQL and Analytics
- Stage D — Honest Feature Table
- Stage E — Leakage Experiments

## Repository Structure

- `data/` — Raw project data (git-ignored)
- `src/` — Python source code
- `sql/` — Database schema and SQL analysis
- `notebooks/` — ML experiments
- `tests/` — Automated tests
- `docs/` — Project documentation

## Database Loading

Stage B implements the PostgreSQL database layer for the agricultural
dataset.

### Database tables

The database contains three related tables:

- `farms` — farm-level information
- `plots` — plot-level information linked to farms
- `harvests` — harvest-level information linked to plots

The relationships are:

farms → plots → harvests

### Data loading

The loading pipeline is implemented in:

`src/load.py`

The loader:

1. Reads the CSV datasets.
2. Converts dates into PostgreSQL-compatible dates.
3. Converts boolean values such as `yes/no` and `true/false`.
4. Converts percentage-formatted slope values.
5. Removes duplicate harvest IDs.
6. Removes harvest records referencing nonexistent plots.
7. Loads farms before plots and plots before harvests.
8. Uses PostgreSQL conflict handling to prevent duplicate primary keys.
9. Uses a database transaction so failures can be rolled back.

### Running the loader

From the repository root:

```bash
python src/load.py

## Stage C — SQL Analysis

### Purpose

Stage C uses PostgreSQL to analyse the cleaned and validated agricultural
data before machine-learning modelling.

The purpose is not only to practise SQL. The SQL analysis helps identify
patterns in the data and provides evidence that will guide feature
selection and the later machine-learning evaluation.

The database contains three related tables:

- `farms` — farm-level information
- `plots` — plot-level information
- `harvests` — seasonal harvest information

The relationships are:

`farms → plots → harvests`

using:

- `farms.farm_id = plots.farm_id`
- `plots.plot_id = harvests.plot_id`

### SQL Exercises

The file `sql/exercises.sql` contains 25 SQL exercises arranged from
basic to advanced difficulty.

The exercises cover:

1. Basic `SELECT` queries
2. `WHERE` filtering
3. Multiple filtering conditions
4. `ORDER BY`
5. `LIMIT`
6. `COUNT`
7. Aggregate functions
8. `GROUP BY`
9. `HAVING`
10. Multiple aggregations
11. `INNER JOIN`
12. `LEFT JOIN`
13. `RIGHT JOIN`
14. `FULL OUTER JOIN`
15. Three-table joins
16. Subqueries
17. Correlated subqueries
18. `CASE` expressions
19. `NULL` behaviour in aggregates
20. Aggregation with joins
21. Common Table Expressions (CTEs)
22. `UNION`
23. `INTERSECT`
24. `EXCEPT`
25. Window functions

These exercises demonstrate the SQL skills required to work with the
relational dataset and progressively increase in complexity.

### Analytical Queries

The file `sql/analytics.sql` contains the five required analytical
queries.

#### 1. Target attainment per season

This query calculates the number of harvests, number of successful
harvests, and percentage of harvests that met the target for each season.

This helps identify whether target attainment changes across seasons.

#### 2. Mean yield per crop per division

This analysis calculates mean yield for each crop within each division
and uses a window function to compare the crop-level result with the
division-level mean.

#### 3. Top three plots by yield within each crop

A window function is used to rank plots by yield within each crop.
The analysis returns the top three plots for each crop.

#### 4. Season-over-season change

The `LAG()` window function is used to compare target attainment between
successive seasons.

This analysis is particularly important for the later machine-learning
evaluation because temporal patterns can affect how well a model
generalises to future seasons.

#### 5. Subquery rewritten using CTEs

A nested-subquery analysis is also implemented using Common Table
Expressions.

The two approaches demonstrate how the same analytical problem can be
written using different SQL structures.

### Query Performance

`EXPLAIN ANALYZE` is used to inspect query execution before and after
creating an index on:

`harvests(plot_id)`

The purpose is to demonstrate how database indexing can affect query
execution and to document the performance impact rather than assuming
that an index automatically makes every query faster.

### Data Quality Findings

The data loaded into PostgreSQL contains:

- 420 farms
- 1,817 plots
- 11,385 valid harvest records

During loading:

- 80 duplicate harvest records were removed.
- 250 harvest records referencing invalid plot IDs were removed.

The duplicate checks performed during analysis found:

- 0 duplicate farm IDs
- 0 duplicate plot IDs
- 0 duplicate harvest IDs

Missing-value analysis identified:

| Table | Column | Missing | Percentage |
|---|---|---:|---:|
| farms | `extension_visits_yr` | 46 | 10.95% |
| farms | `household_size` | 42 | 10.00% |
| plots | `slope_pct` | 629 | 34.62% |
| harvests | `fertiliser_kg_ha` | 585 | 5.14% |

All other inspected columns contain no missing values.

### Machine-Learning Target

The machine-learning target is:

`met_target`

It is a Boolean classification target.

Current target distribution:

| Outcome | Records | Percentage |
|---|---:|---:|
| `True` | 6,991 | 61.41% |
| `False` | 4,394 | 38.59% |

The target contains no missing values and is stored as a Boolean value.

A majority-class baseline would predict `True` for every observation and
achieve approximately 61.41% accuracy. Model performance must therefore
be evaluated against an appropriate baseline rather than interpreting
accuracy alone.

### Important Prediction Constraint

The project predicts whether a plot will meet its yield target **at
planting time**.

Therefore, not every column in the database is automatically a valid
machine-learning feature.

Features must be classified according to when the information becomes
available:

- information available at planting time
- information available only after harvest
- target variable

This distinction is essential because using information that becomes
available only after the outcome is known can create data leakage.

The feature-timing decisions are documented separately in:

`docs/feature_timing.md`

The later modelling stage will deliberately demonstrate the difference
between a model containing future/leaky information and an honest model
using only information available at prediction time.

### Reproducibility

The SQL analysis can be reproduced using:

```text
sql/exercises.sql
sql/analytics.sql