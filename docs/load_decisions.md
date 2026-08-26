# Stage B — Database Loading Decisions

## Overview

Stage B implements the PostgreSQL database schema and data-loading pipeline
for the agricultural dataset.

The database contains three related tables:

- `farms`
- `plots`
- `harvests`

The relationships are:

farms → plots → harvests

## Loading Order

Data is loaded in dependency order:

1. Farms
2. Plots
3. Harvests

This order is required because plots reference farms through `farm_id`,
while harvests reference plots through `plot_id`.

## Data Cleaning

### Dates

Harvest planting and harvest dates are converted from the following
supported formats:

- `YYYY-MM-DD`
- `DD-MM-YYYY`
- `MM-DD-YYYY`

Invalid date formats raise an error rather than silently being accepted.

### Boolean Values

Boolean fields accept:

- `yes`
- `true`
- `1`
- `no`
- `false`
- `0`

Values are converted into Python boolean values before insertion.

### Slope

The `slope_pct` field may contain percentage signs.

For example:

`16.8%`

is converted to:

`16.8`

before loading into PostgreSQL.

### Missing Values

Pandas missing values are converted to Python `None`, allowing PostgreSQL
to store them as SQL `NULL`.

## Harvest Data Quality

Duplicate harvest records are identified using `harvest_id`.

The first occurrence is retained and subsequent duplicates are removed.

Harvest records whose `plot_id` does not exist in the plots dataset are
treated as orphan records and removed before loading.

## Data Quality Results

The source harvest dataset contained:

- 11,715 harvest rows

During cleaning:

- 80 duplicate harvest rows were removed
- 250 orphan harvest rows were removed

Therefore:

11,715 - 80 - 250 = 11,385

valid harvest rows were loaded.

The loaded datasets contained:

- 420 farms
- 1,817 plots
- 11,385 harvests

## Idempotency

The loader uses PostgreSQL `ON CONFLICT DO NOTHING` for primary-key
conflicts.

The loader was executed twice using the same source data.

The database row counts remained unchanged:

- Farms: 420
- Plots: 1,817
- Harvests: 11,385

This demonstrates that repeated execution does not create duplicate
database records.

## Transaction Handling

The complete loading process is committed as a transaction.

If an error occurs during loading, the transaction is rolled back so that
partial changes are not left in the database.

## Credentials

Database credentials are supplied through environment variables and are
not stored in the repository.

The raw datasets are also excluded from Git using `.gitignore`.