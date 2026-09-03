# Evaluation Protocol

## Purpose

This document defines the leakage-aware evaluation protocol for the
`met_target` prediction task.

The goal is to estimate model performance under conditions that resemble
real deployment and to identify sources of overly optimistic evaluation.

---

## 1. Target Leakage

Two feature sets were compared:

- **Honest features:** variables available at prediction time.
- **Leaky features:** honest features plus harvest-time and post-outcome
  variables.

The leaky feature set included:

- `harvest_date`
- `rainfall_mm`
- `fertiliser_kg_ha`
- `labour_days`
- `yield_kg_ha`
- `buyer_grade`
- `post_harvest_loss_pct`

### Results

| Metric | Honest | Leaky |
|---|---:|---:|
| Accuracy | 0.6010 | 1.0000 |
| Precision | 0.6018 | 1.0000 |
| Recall | 0.9782 | 1.0000 |
| F1 | 0.7452 | 1.0000 |
| ROC-AUC | 0.5754 | 1.0000 |

The leaky model achieved perfect performance.

Further analysis showed that `buyer_grade` perfectly determines
`met_target`: grade A corresponds to `met_target=True`, while grades B and C
correspond to `met_target=False`.

### Decision

Harvest-time and post-outcome variables must not be used for prediction.

In particular, `buyer_grade`, `yield_kg_ha`, and
`post_harvest_loss_pct` are excluded from the honest feature set.

---

## 2. Train-Test Contamination

Two preprocessing strategies were compared:

1. **Wrong:** preprocessing was fitted using the full dataset before splitting.
2. **Right:** preprocessing was fitted using only the training data.

### Results

| Metric | Wrong | Right |
|---|---:|---:|
| Accuracy | 0.5996 | 0.6010 |
| ROC-AUC | 0.5742 | 0.5754 |

The numerical difference was very small in this dataset.

### Decision

Even when the observed effect is small, preprocessing must be fitted only
on the training data. Test data must remain completely unseen during model
development.

Preprocessing is therefore kept inside the modelling pipeline.

---

## 3. Group Leakage

Farms contain multiple plots and harvest observations. Therefore, randomly
splitting individual observations can place observations from the same farm
in both training and validation sets.

Two approaches were compared:

- Random `StratifiedKFold`
- `StratifiedGroupKFold` grouped by `farm_id`

### Results

| Metric | Random K-Fold | Group K-Fold |
|---|---:|---:|
| Accuracy | 0.6625 | 0.6172 |
| ROC-AUC | 0.8216 | 0.5663 |

Random K-Fold substantially overestimated ROC-AUC.

### Decision

Validation must be grouped by `farm_id` when evaluating generalisation to
unseen farms.

`StratifiedGroupKFold` is therefore the preferred validation strategy for
the main model evaluation.

---

## 4. Temporal Leakage

Agricultural observations have a time dimension. Randomly mixing observations
from different periods can allow information from later periods to influence
evaluation of earlier periods.

Two approaches were compared:

- Random `StratifiedKFold`
- Time-ordered `TimeSeriesSplit`

### Results

| Metric | Random K-Fold | TimeSeriesSplit |
|---|---:|---:|
| Accuracy | 0.6628 | 0.6486 |
| ROC-AUC | 0.8230 | 0.7910 |

Random K-Fold produced higher performance than the time-ordered evaluation.

### Decision

When the intended deployment scenario is prediction of future observations,
validation should preserve temporal order.

`TimeSeriesSplit` is therefore preferred for temporal forecasting evaluation.

---

## 5. Nested Cross-Validation

Nested cross-validation was used to separate hyperparameter tuning from
final performance evaluation.

The inner loop selected hyperparameters, while the outer loop evaluated the
selected model on an untouched validation fold.

### Nested CV Results

| Outer Fold | ROC-AUC |
|---|---:|
| 1 | 0.5798 |
| 2 | 0.6058 |
| 3 | 0.5844 |
| 4 | 0.5336 |
| 5 | 0.5295 |

Mean ROC-AUC:

**0.5666**

Standard deviation:

**0.0300**

### Single-Loop Comparison

| Evaluation | ROC-AUC |
|---|---:|
| Single-loop CV | 0.566592 |
| Nested CV | 0.566607 |
| Difference | -0.000015 |

The difference was effectively zero for this dataset.

The result should not be interpreted as evidence that single-loop tuning is
always unbiased. Nested CV remains the more rigorous approach because it
separates hyperparameter selection from outer performance estimation.

---

## 6. Learning Curve and Bias-Variance Analysis

Learning-curve ROC-AUC results:

| Training Size | Training ROC-AUC | Validation ROC-AUC |
|---:|---:|---:|
| 911 | 0.9524 | 0.5238 |
| 2963 | 0.9197 | 0.5353 |
| 5014 | 0.9195 | 0.5405 |
| 7066 | 0.9108 | 0.5510 |
| 9118 | 0.9007 | 0.5663 |

Training performance remained high while validation performance was much
lower.

This large and persistent gap indicates high variance and overfitting.

Validation ROC-AUC improved as more training data was added, but the gap
between training and validation performance remained substantial.

### Interpretation

The model is primarily affected by variance rather than high bias.

Potential responses include:

- stronger model regularisation;
- simpler models;
- improved feature engineering;
- additional training data;
- continued leakage-aware validation.

---

## 7. Recommended Evaluation Protocol

The following protocol should be used for future model evaluation.

### Feature policy

Only features available at the prediction point may be used.

Harvest-time and post-outcome variables must be excluded unless the deployment
scenario explicitly makes them available before prediction.

### Preprocessing

All learned preprocessing operations must be fitted on training data only.

Use a scikit-learn `Pipeline` and `ColumnTransformer` so that preprocessing
is performed separately inside each training fold.

### Grouping

For evaluation of generalisation to unseen farms, use:

`StratifiedGroupKFold`

with `farm_id` as the grouping variable.

### Temporal evaluation

For future-oriented prediction, preserve chronological order and use:

`TimeSeriesSplit`

where appropriate.

### Hyperparameter tuning

Use nested cross-validation when an unbiased estimate of generalisation
performance is required after hyperparameter selection.

### Primary metric

ROC-AUC is used as the primary discrimination metric because the target is
binary and class proportions are not perfectly balanced.

Accuracy, precision, recall, and F1 should be reported as complementary
metrics.

---

## 8. Final Model Assessment

The honest Random Forest performed substantially worse than models evaluated
under leakage-prone procedures.

Earlier honest-model evaluation produced approximately:

- Accuracy: 0.5982
- Precision: 0.6183
- Recall: 0.8528
- F1: 0.7169
- ROC-AUC: 0.5914

The more rigorous grouped nested-CV estimate was lower:

**Mean ROC-AUC = 0.5666 (SD = 0.0300).**

This indicates that the model has limited discriminative performance when
evaluation is performed under stricter leakage-aware conditions.

The realistic grouped evaluation should therefore be preferred over
random observation-level validation results.

---

## 9. Rules for Future Experiments

Before reporting model performance:

1. Define which variables are available at prediction time.
2. Remove harvest-time and post-outcome variables.
3. Split data before fitting learned preprocessing.
4. Keep preprocessing inside the modelling pipeline.
5. Group observations by `farm_id` when testing unseen-farm generalisation.
6. Preserve temporal order when predicting future observations.
7. Keep the final test/evaluation data untouched during tuning.
8. Use nested CV when hyperparameter-selection bias must be controlled.
9. Report mean and standard deviation across validation folds.
10. Document any assumptions about prediction timing and deployment.