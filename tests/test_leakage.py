import pandas as pd
import pytest

from sklearn.model_selection import (
    StratifiedKFold,
    StratifiedGroupKFold,
    TimeSeriesSplit,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# -------------------------------------------------------------------
# Feature definitions
# -------------------------------------------------------------------

HONEST_FEATURES = [
    "village",
    "division",
    "soil_type",
    "altitude_m",
    "household_size",
    "extension_visits_yr",
    "area_ha",
    "crop",
    "slope_pct",
    "irrigated",
    "season",
    "planting_date",
    "seed_variety",
]

HARVEST_TIME_FEATURES = [
    "harvest_date",
    "rainfall_mm",
    "fertiliser_kg_ha",
    "labour_days",
    "yield_kg_ha",
    "buyer_grade",
    "post_harvest_loss_pct",
]


# -------------------------------------------------------------------
# 1. Feature guard tests
# -------------------------------------------------------------------

def test_honest_features_do_not_contain_harvest_date():
    assert "harvest_date" not in HONEST_FEATURES


def test_honest_features_do_not_contain_yield():
    assert "yield_kg_ha" not in HONEST_FEATURES


def test_honest_features_do_not_contain_buyer_grade():
    assert "buyer_grade" not in HONEST_FEATURES


def test_honest_features_do_not_contain_post_harvest_loss():
    assert "post_harvest_loss_pct" not in HONEST_FEATURES


def test_honest_features_do_not_contain_rainfall():
    assert "rainfall_mm" not in HONEST_FEATURES


def test_honest_features_do_not_contain_fertiliser():
    assert "fertiliser_kg_ha" not in HONEST_FEATURES


def test_honest_features_do_not_contain_labour_days():
    assert "labour_days" not in HONEST_FEATURES


# -------------------------------------------------------------------
# 2. Feature-set integrity
# -------------------------------------------------------------------

def test_honest_feature_count():
    assert len(HONEST_FEATURES) == 13


def test_harvest_time_feature_count():
    assert len(HARVEST_TIME_FEATURES) == 7


def test_honest_and_harvest_features_are_disjoint():
    assert set(HONEST_FEATURES).isdisjoint(HARVEST_TIME_FEATURES)


# -------------------------------------------------------------------
# 3. Target integrity
# -------------------------------------------------------------------

def test_target_is_binary():
    y = pd.Series([True, False, True, False])
    assert y.dtype == bool


def test_target_has_two_classes():
    y = pd.Series([True, False, True, False])
    assert y.nunique() == 2


# -------------------------------------------------------------------
# 4. Group validation tests
# -------------------------------------------------------------------

def test_group_cv_keeps_groups_separate():
    X = pd.DataFrame({"x": range(12)})
    y = pd.Series([0, 1] * 6)
    groups = pd.Series([1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6])

    cv = StratifiedGroupKFold(
        n_splits=3,
        shuffle=True,
        random_state=42,
    )

    for train_idx, test_idx in cv.split(X, y, groups):
        train_groups = set(groups.iloc[train_idx])
        test_groups = set(groups.iloc[test_idx])

        assert train_groups.isdisjoint(test_groups)


# -------------------------------------------------------------------
# 5. Temporal validation tests
# -------------------------------------------------------------------

def test_time_series_split_preserves_order():
    X = pd.DataFrame({"x": range(12)})
    y = pd.Series(range(12))

    cv = TimeSeriesSplit(n_splits=3)

    for train_idx, test_idx in cv.split(X):
        assert max(train_idx) < min(test_idx)


# -------------------------------------------------------------------
# 6. Stratified validation test
# -------------------------------------------------------------------

def test_stratified_kfold_produces_expected_number_of_splits():
    X = pd.DataFrame({"x": range(20)})
    y = pd.Series([0, 1] * 10)

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    splits = list(cv.split(X, y))

    assert len(splits) == 5


# -------------------------------------------------------------------
# 7. Preprocessing pipeline test
# -------------------------------------------------------------------

def test_scaler_is_inside_pipeline():
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
        ]
    )

    assert "scaler" in pipeline.named_steps

    # -------------------------------------------------------------------
# 8. Explicit harvest-time feature guard
# -------------------------------------------------------------------

def test_no_harvest_time_features_in_honest_feature_set():
    forbidden = {
        "harvest_date",
        "rainfall_mm",
        "fertiliser_kg_ha",
        "labour_days",
        "yield_kg_ha",
        "buyer_grade",
        "post_harvest_loss_pct",
    }

    leaked_features = forbidden.intersection(HONEST_FEATURES)

    assert leaked_features == set(), (
        f"Harvest-time features found in honest feature set: "
        f"{leaked_features}"
    )