# Skye8 Data Science / ML Internship

## Project 1 — How Models Lie

This repository contains my implementation of Skye8 Project Brief 1:

> How Models Lie: An Evaluation Protocol Built From Failures

## Objective

The project demonstrates how incorrect machine-learning evaluation can produce misleadingly high performance estimates.

The project investigates:

1. Target leakage
2. Train-test contamination
3. Group leakage
4. Temporal leakage

It then develops an evaluation protocol designed to prevent these problems in future ML projects.

## Repository Structure

```text
data/          Raw project data (git-ignored)
src/            Python source code
sql/            Database schema and SQL analysis
notebooks/      ML experiments
tests/          Automated tests
docs/           Project documentation
README.md       Project documentation
requirements.txt Python dependencies
.gitignore      Git ignore rules