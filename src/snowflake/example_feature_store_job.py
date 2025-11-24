# ============================================================
# FILE: src/your_project_name/config/__init__.py
# ============================================================

import yaml
from pathlib import Path

def load_config(filename: str):
    path = Path(__file__).parent / filename
    with open(path, "r") as f:
        return yaml.safe_load(f)



# ============================================================
# FILE: src/your_project_name/config/features_store.yaml
# (YAML — put this into the actual YAML file, not Python)
# ============================================================

"""
features:
  deposit:
    earliest_feature_date: "2020-01-01"
    max_daily_lag_days: 1
    rerun_last_n_days: 0
"""



# ============================================================
# FILE: src/your_project_name/features/date_logic.py
# ============================================================

from datetime import date, timedelta
from typing import List, Optional

from snowflake.snowpark import Session
from snowflake.snowpark import functions as F


def get_snowflake_today(session: Session) -> date:
    """
    Using Snowflake's CURRENT_DATE ensures timezone alignment
    with the Snowflake Task runtime.
    """
    return session.sql("SELECT CURRENT_DATE() AS TODAY").collect()[0]["TODAY"]


def get_feature_dates_to_run(
    session: Session,
    population_table: str,
    feature_table: str,
    earliest_feature_date: date,
    max_daily_lag_days: int = 1,
    rerun_last_n_days: int = 0,
) -> List[date]:
    """
    Determine which feature_date values to process.

    This supports:
      - Initial backfill from earliest_feature_date
      - Catching missing days in the feature table
      - Automatically reprocessing the last N days (optional)
    """

    sf_today = get_snowflake_today(session)
    target_end_date = sf_today - timedelta(days=max_daily_lag_days)

    if earliest_feature_date > target_end_date:
        return []

    # Rerun window (only if rerun_last_n_days > 0)
    if rerun_last_n_days > 0:
        rerun_start_date = target_end_date - timedelta(days=rerun_last_n_days - 1)
    else:
        rerun_start_date = target_end_date + timedelta(days=1)

    # ----- Get all POPULATION dates -----
    pop_dates = (
        session.table(population_table)
        .select(F.col("POPULATION_DATE").alias("FEATURE_DATE"))
        .distinct()
        .filter(
            (F.col("FEATURE_DATE") >= F.lit(earliest_feature_date))
            & (F.col("FEATURE_DATE") <= F.lit(target_end_date))
        )
    )

    # ----- Get all FEATURE dates -----
    feat_dates = (
        session.table(feature_table)
        .select("FEATURE_DATE")
        .distinct()
        .filter(
            (F.col("FEATURE_DATE") >= F.lit(earliest_feature_date))
            & (F.col("FEATURE_DATE") <= F.lit(target_end_date))
        )
    )

    # ----- Anti-join: Find missing dates and rerun recent ones -----
    joined = (
        pop_dates.alias("p")
        .join(
            feat_dates.alias("f"),
            on=F.col("p.FEATURE_DATE") == F.col("f.FEATURE_DATE"),
            how="left",
        )
        .select(
            F.col("p.FEATURE_DATE").alias("FEATURE_DATE"),
            F.col("f.FEATURE_DATE").alias("HAS_FEATURE_DATE"),
        )
    )

    to_run = (
        joined.filter(
            (F.col("HAS_FEATURE_DATE").is_null())  # missing
            | (F.col("FEATURE_DATE") >= F.lit(rerun_start_date))  # forced rerun
        )
        .select("FEATURE_DATE")
        .sort("FEATURE_DATE")
        .collect()
    )

    return [r["FEATURE_DATE"] for r in to_run]



# ============================================================
# FILE: src/your_project_name/features/feature_writer.py
# ============================================================

from datetime import date
from snowflake.snowpark import Session, DataFrame
from snowflake.snowpark import functions as F


def delete_feature_date(session: Session, feature_table: str, feature_date: date):
    session.table(feature_table).delete(
        F.col("FEATURE_DATE") == F.lit(feature_date)
    )


def write_feature_date(
    session: Session,
    feature_table: str,
    features_df: DataFrame,
    feature_date: date,
    *,
    skip_if_empty: bool = True,
):
    """
    Safely writes a single day's features (idempotent).
    DELETE + INSERT ensures clean retries.
    """
    if skip_if_empty and features_df.count() == 0:
        return

    delete_feature_date(session, feature_table, feature_date)

    features_df.write.mode("append").save_as_table(feature_table)



# ============================================================
# FILE: jobs/features/snowflake/write_deposit_features_production.py
# ============================================================

"""
Main Snowpark Feature Store Job for Deposit Features

This job:
  - Loads config (features_store.yaml)
  - Determines which feature_date values to compute
  - Builds raw Snowpark DF for each date
  - Calls your existing transformations (not included here)
  - Writes results idempotently via DELETE + INSERT
"""

from datetime import date
from typing import Optional

from snowflake.snowpark import Session
from snowflake.snowpark import functions as F

from your_project_name.config import load_config
from your_project_name.features.date_logic import get_feature_dates_to_run
from your_project_name.features.feature_writer import write_feature_date

# NOTE: You already have expressions and transformations in your repo.
# We omit them per your request, but you would import your transformation here.
# from your_project_name.features.transformation import build_deposit_features_df


POP_TABLE = "POP_ACTIVE_ACCOUNTS_DAILY"
TXN_TABLE = "DEPOSIT_TRANSACTIONS"
FEATURE_TABLE = "FEAT_DEPOSIT_DAILY"


def build_raw_deposit_df_for_date(session: Session, feature_date: date):
    """
    Builds the raw Snowpark DataFrame (population + transactions).
    You can adjust windows, source tables, or joins here.
    """

    pop_df = (
        session.table(POP_TABLE)
        .filter(
            (F.col("POPULATION_DATE") == F.lit(feature_date))
            & (F.col("IS_ACTIVE") == F.lit(True))
        )
        .select("POPULATION_DATE", "ACCOUNT_ID")
    )

    txn_df = (
        session.table(TXN_TABLE)
        .filter(
            (F.col("POST_DATE") <= F.lit(feature_date))
            & (F.col("POST_DATE") > F.dateadd("day", -30, F.lit(feature_date)))
        )
        .select("ACCOUNT_ID", "POST_DATE", "DEPOSIT_AMOUNT")
    )

    return pop_df.join(txn_df, on="ACCOUNT_ID", how="left")


def write_deposit_features_for_date(session: Session, feature_date: date):
    """
    Per-date write wrapper.
    Uses your existing transformation layer.
    """

    raw_df = build_raw_deposit_df_for_date(session, feature_date)

    # Use your actual transformation function here:
    # features_df = build_deposit_features_df(raw_df)
    #
    # For now, placeholder:
    features_df = raw_df  # <--- replace with real transformation

    write_feature_date(session, FEATURE_TABLE, features_df, feature_date)


def run_deposit_feature_job(session: Session, target_end_date_str: Optional[str] = None) -> str:
    """
    Snowflake Stored Procedure Handler.

    Wire to a Snowflake Task:
        CREATE TASK ... AS CALL run_deposit_feature_job();
    """

    cfg = load_config("features_store.yaml")["features"]["deposit"]

    earliest_date = date.fromisoformat(cfg["earliest_feature_date"])

    feature_dates = get_feature_dates_to_run(
        session=session,
        population_table=POP_TABLE,
        feature_table=FEATURE_TABLE,
        earliest_feature_date=earliest_date,
        max_daily_lag_days=cfg.get("max_daily_lag_days", 1),
        rerun_last_n_days=cfg.get("rerun_last_n_days", 0),
    )

    for feature_date in feature_dates:
        write_deposit_features_for_date(session, feature_date)

    if not feature_dates:
        return "No feature dates to process."

    return "Processed feature dates: " + ", ".join(str(d) for d in feature_dates)
