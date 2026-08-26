import pandas as pd
import psycopg2

from datetime import datetime
from pathlib import Path

from db import DB_CONFIG


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

FARMS_FILE = DATA_DIR / "farms.csv"
PLOTS_FILE = DATA_DIR / "plots.csv"
HARVESTS_FILE = DATA_DIR / "harvests.csv"

def to_native(rows):
    """
    Convert numpy/pandas scalar types (e.g. numpy.float64, numpy.int64)
    into native Python types, and any pandas missing-value sentinel
    (pd.NA, NaT, NaN) into None, so psycopg2 adapts every value correctly.
    """
    def convert(v):
        if v is None:
            return None
        if hasattr(v, "item"):
            return v.item()
        if pd.isna(v):
            return None
        return v

    return [tuple(convert(v) for v in row) for row in rows]


def flexible_date(date_str):
    """
    Convert supported date formats into a Python date object.

    Supported formats:
        YYYY-MM-DD
        DD-MM-YYYY
        MM-DD-YYYY
    """

    if pd.isna(date_str):
        return None

    formats = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%Y/%m/%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d %b %Y",
]

    for fmt in formats:
        try:
            return datetime.strptime(
                str(date_str).strip(),
                fmt
            ).date()

        except ValueError:
            continue

    raise ValueError(f"Invalid date format: {date_str}")


def flexible_bool(val):
    """
    Convert common boolean representations into Python booleans.
    """

    if pd.isna(val):
        return None

    truthy = {"yes", "true", "1"}
    falsey = {"no", "false", "0"}

    value = str(val).strip().lower()

    if value in truthy:
        return True

    if value in falsey:
        return False

    raise ValueError(
        f"Unrecognized boolean format: {val}"
    )


def replace_missing_values(df):
    """
    Convert Pandas missing values (NaN/NaT) into Python None
    so PostgreSQL receives SQL NULL.
    """

    return df.where(pd.notna(df), None)


def load_farms(conn, file_path):
    """
    Load farms.csv into the farms table.
    """

    df = pd.read_csv(file_path)

    df = replace_missing_values(df)

    rows = to_native(
    list(
        df.itertuples(
            index=False,
            name=None
        )
    )
)

    cur = conn.cursor()

    cur.executemany(
        """
        INSERT INTO farms (
            farm_id,
            village,
            division,
            soil_type,
            altitude_m,
            household_size,
            extension_visits_yr
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (farm_id) DO NOTHING
        """,
        rows,
    )

    cur.close()

    print(
        f"Successfully processed {len(rows)} farm rows"
    )


def load_plots(conn, file_path):
    """
    Load plots.csv into the plots table.

    Cleans slope percentages and boolean irrigation values.
    """

    df = pd.read_csv(file_path)

    # Convert slope percentages such as "16.8%" to 16.8
    if "slope_pct" in df.columns:

        clean_slope = (
            df["slope_pct"]
            .astype("string")
            .str.replace("%", "", regex=False)
        )

        df["slope_pct"] = pd.to_numeric(clean_slope, errors="coerce").astype("float64")

    # Convert irrigation values to proper booleans
    df["irrigated"] = (
        df["irrigated"]
        .apply(flexible_bool)
    )

    df = replace_missing_values(df)

    rows = to_native(
    list(
        df.itertuples(
            index=False,
            name=None
        )
    )
)

    cur = conn.cursor()

    cur.executemany(
        """
        INSERT INTO plots (
            plot_id,
            farm_id,
            area_ha,
            crop,
            slope_pct,
            irrigated
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (plot_id) DO NOTHING
        """,
        rows,
    )

    cur.close()

    print(
        f"Successfully processed {len(rows)} plot rows"
    )


def load_harvests(conn, file_path, plot_path):
    """
    Load harvests.csv into the harvests table.

    Handles:
    - multiple date formats
    - boolean representations
    - duplicate harvest IDs
    - orphan plot references
    """

    df = pd.read_csv(file_path)

    # Convert dates
    df["planting_date"] = (
        df["planting_date"]
        .apply(flexible_date)
    )

    df["harvest_date"] = (
        df["harvest_date"]
        .apply(flexible_date)
    )

    # Convert boolean values
    df["met_target"] = (
        df["met_target"]
        .apply(flexible_bool)
    )

    # Remove duplicate harvest IDs.
    # Keep the first occurrence.
    duplicate_mask = df.duplicated(
        subset="harvest_id",
        keep="first"
    )

    duplicate_rows = df[duplicate_mask]

    df = df[~duplicate_mask]

    # Load valid plot IDs
    plots_df = pd.read_csv(plot_path)

    valid_plot_ids = set(
        plots_df["plot_id"].dropna()
    )

    # Identify orphan harvests
    orphan_mask = ~df["plot_id"].isin(
        valid_plot_ids
    )

    orphan_rows = df[orphan_mask]

    df = df[~orphan_mask]

    print(
        f"{len(duplicate_rows)} duplicate harvest rows dropped"
    )

    print(
        f"{len(orphan_rows)} orphan harvest rows dropped"
    )

    print(
        f"{len(df)} harvest rows will be loaded"
    )

    # Convert remaining missing values to None
    df = replace_missing_values(df)

    rows = to_native(
    list(
        df.itertuples(
            index=False,
            name=None
        )
    )
)

    cur = conn.cursor()

    cur.executemany(
        """
        INSERT INTO harvests (
            harvest_id,
            plot_id,
            season,
            planting_date,
            harvest_date,
            rainfall_mm,
            fertiliser_kg_ha,
            seed_variety,
            labour_days,
            yield_kg_ha,
            buyer_grade,
            post_harvest_loss_pct,
            met_target
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (harvest_id) DO NOTHING
        """,
        rows,
    )

    cur.close()

    print(
        f"Successfully processed {len(rows)} harvest rows"
    )


def main():

    conn = None

    try:

        print("Connecting to PostgreSQL...")

        conn = psycopg2.connect(
            **DB_CONFIG
        )

        print("Database connection successful.")

        # Parent table first
        load_farms(
            conn,
            FARMS_FILE
        )

        # Child table second
        load_plots(
            conn,
            PLOTS_FILE
        )

        # Harvests depend on plots
        load_harvests(
            conn,
            HARVESTS_FILE,
            PLOTS_FILE
        )

        # Commit everything together
        conn.commit()

        print("Database load completed successfully.")

    except Exception:

        if conn is not None:
            conn.rollback()

        print(
            "Database load failed. "
            "All changes have been rolled back."
        )

        raise

    finally:

        if conn is not None:
            conn.close()

            print(
                "Database connection closed."
            )


if __name__ == "__main__":
    main()