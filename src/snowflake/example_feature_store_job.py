from datetime import date, timedelta
from typing import List, Optional

from snowflake.snowpark import Session
from snowflake.snowpark import functions as F


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

POP_TABLE = "POP_ACTIVE_ACCOUNTS_DAILY"
FEATURE_TABLE = "FEAT_DEPOSIT_DAILY"

# Usually you want to run through "yesterday" so your sources are stable
DEFAULT_MAX_LAG_DAYS = 1


# ---------------------------------------------------------------------------
# Helpers to find which dates need to run
# ---------------------------------------------------------------------------

def get_snowflake_today(session: Session) -> date:
    """Return current_date() as a Python date via Snowflake."""
    df = session.sql("SELECT CURRENT_DATE() AS TODAY")
    return df.collect()[0]["TODAY"]


def get_last_feature_date(session: Session) -> Optional[date]:
    """
    Return MAX(feature_date) from the feature table.
    If the table is empty, return None.
    """
    df = session.table(FEATURE_TABLE).select(F.max("FEATURE_DATE").alias("LAST_FEATURE_DATE"))
    row = df.collect()[0]
    return row["LAST_FEATURE_DATE"]  # date or None


def get_first_population_date(session: Session) -> date:
    """Return MIN(population_date) from the population table."""
    df = session.table(POP_TABLE).select(F.min("POPULATION_DATE").alias("FIRST_POP_DATE"))
    row = df.collect()[0]
    return row["FIRST_POP_DATE"]


def get_dates_to_run(
    session: Session,
    target_end_date: Optional[date] = None,
    max_lag_days: int = DEFAULT_MAX_LAG_DAYS,
) -> List[date]:
    """
    Decide which dates we need to process:
      - Start just after the last_feature_date (or from first population date if none)
      - End at target_end_date (or CURRENT_DATE - max_lag_days)
      - Use population table as the source of truth for which dates exist
    """
    if target_end_date is None:
        sf_today = get_snowflake_today(session)
        target_end_date = sf_today - timedelta(days=max_lag_days)

    last_feature_date = get_last_feature_date(session)

    if last_feature_date is None:
        # No features yet: start from one day before the first population date
        first_pop_date = get_first_population_date(session)
        last_feature_date = first_pop_date - timedelta(days=1)

    # Get distinct population dates that are:
    #  > last_feature_date and <= target_end_date
    pop_dates_df = (
        session.table(POP_TABLE)
        .select(F.col("POPULATION_DATE").alias("RUN_DATE"))
        .distinct()
        .filter(
            (F.col("RUN_DATE") > F.lit(last_feature_date)) &
            (F.col("RUN_DATE") <= F.lit(target_end_date))
        )
        .sort("RUN_DATE")
    )

    rows = pop_dates_df.collect()
    return [r["RUN_DATE"] for r in rows]


# ---------------------------------------------------------------------------
# Feature building logic (Snowpark)
# ---------------------------------------------------------------------------

def build_deposit_features_df(session: Session, feature_date: date):
    """
    Core business logic for one feature_date using Snowpark.
    This is where you join your source tables and compute aggregations.

    For now this is a simple example using just the population table.
    Replace the placeholder logic with your real feature pipeline.
    """

    pop_df = (
        session.table(POP_TABLE)
        .filter(
            (F.col("POPULATION_DATE") == F.lit(feature_date)) &
            (F.col("IS_ACTIVE") == F.lit(True))
        )
        .select(
            F.col("POPULATION_DATE").alias("FEATURE_DATE"),
            F.col("ACCOUNT_ID"),
            # Example placeholder features:
            # F.lit(1).alias("num_deposits_last_30d"),
            # F.lit(0.0).alias("avg_deposit_amount_90d"),
        )
    )

    # TODO: join to your transaction history, balance tables, etc.
    # Example skeleton:
    #
    # txn_df = session.table("TXN_HISTORY").filter(
    #     (F.col("POST_DATE") <= F.lit(feature_date)) &
    #     (F.col("POST_DATE") > F.dateadd("day", -30, F.lit(feature_date)))
    # )
    #
    # features_df = (
    #     pop_df.join(txn_df, on="ACCOUNT_ID", how="left")
    #           .group_by("FEATURE_DATE", "ACCOUNT_ID")
    #           .agg(
    #               F.count("*").alias("num_deposits_last_30d"),
    #               F.avg("AMOUNT").alias("avg_deposit_amount_30d"),
    #           )
    # )

    features_df = pop_df  # replace with real feature_df
    return features_df


# ---------------------------------------------------------------------------
# Write logic: idempotent per-day
# ---------------------------------------------------------------------------

def write_deposit_features_for_date(session: Session, feature_date: date):
    """
    Idempotent per-day load:
      1. Build features_df for that date.
      2. Delete any existing rows in the feature table for that feature_date.
      3. Append the fresh rows.
    """
    features_df = build_deposit_features_df(session, feature_date)

    # If you want a guard against empty populations for some edge day:
    row_count = features_df.count()
    if row_count == 0:
        # Nothing to write for this day; skip
        return

    # Delete old rows for this date (if any) to make this idempotent
    session.table(FEATURE_TABLE).delete(
        F.col("FEATURE_DATE") == F.lit(feature_date)
    )

    # Append new rows for that date
    features_df.write.mode("append").save_as_table(FEATURE_TABLE)


# ---------------------------------------------------------------------------
# Main entrypoint (for stored proc or external driver)
# ---------------------------------------------------------------------------

def run(session: Session, target_end_date_str: Optional[str] = None) -> str:
    """
    Main entrypoint for Snowpark.

    You can register this as a Python stored procedure like:

      CREATE OR REPLACE PROCEDURE WRITE_DEPOSIT_FEATURES()
      RETURNS STRING
      LANGUAGE PYTHON
      RUNTIME_VERSION = '3.10'
      PACKAGES = ('snowflake-snowpark-python')
      HANDLER = 'run'
      AS
      $$  <paste this script>  $$;

    And then wire that proc to a TASK that runs daily.

    target_end_date_str allows you to override the end date
    (e.g., for backfill testing).
    """
    if target_end_date_str:
        target_end_date = date.fromisoformat(target_end_date_str)  # 'YYYY-MM-DD'
    else:
        target_end_date = None

    dates_to_run = get_dates_to_run(session, target_end_date=target_end_date)

    for d in dates_to_run:
        write_deposit_features_for_date(session, d)

    if not dates_to_run:
        msg = "No dates to run; feature table is already up to date."
    else:
        msg = f"Processed feature dates: {', '.join(str(d) for d in dates_to_run)}"

    return msg
