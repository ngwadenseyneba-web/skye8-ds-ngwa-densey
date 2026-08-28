# Feature Timing and Data Leakage

## Purpose

The machine-learning task is to predict `met_target`.

Feature selection must reflect the information that would actually be
available at the time the prediction is made.

Using information that is only known after the outcome occurs would cause
data leakage and produce an unrealistically strong model.

## Prediction Point

The prediction point is the planting-time stage.

The model should therefore primarily use information that is available
at or before planting.

## Feature Timing Assessment

| Feature | Timing | ML Decision | Reason |
|---|---|---|---|
| farm_id | Before planting | Exclude as predictor | Identifier rather than meaningful measurement |
| village | Before planting | Include | Location information is available beforehand |
| division | Before planting | Include | Geographic information is available beforehand |
| soil_type | Before planting | Include | Known farm characteristic |
| altitude_m | Before planting | Include | Physical farm characteristic |
| household_size | Before planting | Include | Farm/household characteristic |
| extension_visits_yr | Timing-dependent | Review | Depends on whether the value represents historical visits or future visits |
| plot_id | Before planting | Exclude as predictor | Identifier rather than a useful explanatory variable |
| area_ha | Before planting | Include | Plot area is known before production |
| crop | At/before planting | Include | Crop choice is known before production |
| slope_pct | Before planting | Include | Plot characteristic |
| irrigated | Before planting | Include | Irrigation status can be known before production |
| season | Before planting | Include | Season is known |
| planting_date | At planting | Include carefully | Known at the prediction point |
| rainfall_mm | Timing-dependent | Review | Must represent rainfall information available at prediction time |
| fertiliser_kg_ha | Timing-dependent | Review | Must only include fertiliser information known at prediction time |
| seed_variety | At planting | Include | Known when the crop is planted |
| labour_days | During production | Exclude | Future information relative to planting |
| harvest_date | After planting | Exclude | Not known at prediction time |
| yield_kg_ha | After harvest | Exclude | Directly related to the eventual outcome |
| buyer_grade | After harvest | Exclude | Known only after production/harvest |
| post_harvest_loss_pct | After harvest | Exclude | Known after harvest |
| met_target | Outcome | Target | This is the variable being predicted |

## Leakage Features

The following variables must not be used by the honest planting-time
model:

- `harvest_date`
- `yield_kg_ha`
- `buyer_grade`
- `post_harvest_loss_pct`
- `labour_days`

These variables contain information that becomes available after the
prediction point.

Using them would allow the model to learn from future information.

## Ambiguous Features

The following variables require special attention:

### extension_visits_yr

The model should only use this feature if it represents information
available before the prediction is made.

### rainfall_mm

Rainfall must be defined according to a period that has already occurred
or is legitimately known at prediction time.

If it represents rainfall accumulated during the growing season, it is
future information and must not be used by the honest model.

### fertiliser_kg_ha

Only fertiliser information known at planting time should be used.

If the variable represents the total amount applied during the entire
growing season, it contains future information and should be excluded
from the honest model.

## Honest Feature Set

The initial honest model will use information that is available at or
before planting, subject to the timing decisions above.

Candidate features include:

- `village`
- `division`
- `soil_type`
- `altitude_m`
- `household_size`
- `area_ha`
- `crop`
- `slope_pct`
- `irrigated`
- `season`
- `planting_date`
- `seed_variety`

The ambiguous variables will only be included if their definitions
confirm that the information is available at prediction time.

## Target

The target variable is:

`met_target`

Distribution:

- `True`: 6,991 records (61.41%)
- `False`: 4,394 records (38.59%)

The target itself must never be included as an input feature.

## Honest vs Leaky Modelling

Two feature sets will be considered during modelling:

### Honest model

Uses only information legitimately available at the prediction point.

### Leaky model

May include selected future information deliberately for demonstration.

The purpose of the leaky model is not to produce the final model.

It demonstrates how data leakage can produce artificially strong
performance and why feature timing matters.

The final recommended model must use the honest feature set.
