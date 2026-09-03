# Validation Strategy

## Group Validation

Farm-level grouping is required because multiple observations can belong to the same farm.

Random stratified validation allows the same farms to appear in training and validation sets and therefore gives overly optimistic estimates.

## Temporal Validation

For future prediction, validation should respect planting-date order.

TimeSeriesSplit provides a more realistic estimate than randomly mixing earlier and later observations.

## Nested Cross-Validation

Nested cross-validation was used to separate hyperparameter selection from outer performance estimation.

The nested ROC-AUC mean was approximately 0.5666.
