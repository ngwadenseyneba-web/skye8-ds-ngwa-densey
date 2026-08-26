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