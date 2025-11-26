# =====================================================================
# FILE: src/your_project_name/features/__init__.py
# =====================================================================

"""
Feature package

High-level layout:

- date_logic.py       : Decide which feature_date values to run for the feature store.
- feature_writer.py   : Idempotent per-day writes to Snowflake (DELETE + INSERT).
- ohe.py              : Shared OHE / preprocessing logic for model dev/scoring.
- masking.py          : Shared masking / conditional transforms for model features.
- deposit/            : Deposit-domain feature logic (Snowpark / pandas).
- source_system/      : Source-system-level transforms to build "rawish" DataFrames.
"""

# You can optionally re-export key functions here if you want shorter imports.


# =====================================================================
# FILE: src/your_project_name/features/date_logic.py
# =====================================================================

from datetime import date, timedelta
from typing import List

from snowflake.snowpark import Session
from snowflake.snowpark import functions as F


def get_snowflake_today(session: Session) -> date:
    """
    Use Snowflake's CURRENT_DATE() to stay aligned with Snowflake Task timezone.
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
    Decide which feature_date values to process.

    - Uses population_table as the source of truth for valid dates.
    - Includes any population_date that:
        * is between earliest_feature_date and target_end_date, and
        * is missing from the feature_table, OR
        * falls within the last `rerun_last_n_days` dates (optional forced rerun window).
    """

    sf_today = get_snowflake_today(session)
    target_end_date = sf_today - timedelta(days=max_daily_lag_days)

    if earliest_feature_date > target_end_date:
        return []

    # Compute rerun window for tail days (if enabled)
    if rerun_last_n_days > 0:
        rerun_start_date = target_end_date - timedelta(days=rerun_last_n_days - 1)
    else:
        # Ensure no date satisfies this if rerun_last_n_days == 0
        rerun_start_date = target_end_date + timedelta(days=1)

    # Population dates in range
    pop_dates = (
        session.table(population_table)
        .select(F.col("POPULATION_DATE").alias("FEATURE_DATE"))
        .distinct()
        .filter(
            (F.col("FEATURE_DATE") >= F.lit(earliest_feature_date))
            & (F.col("FEATURE_DATE") <= F.lit(target_end_date))
        )
    )

    # Existing feature dates in range
    feat_dates = (
        session.table(feature_table)
        .select("FEATURE_DATE")
        .distinct()
        .filter(
            (F.col("FEATURE_DATE") >= F.lit(earliest_feature_date))
            & (F.col("FEATURE_DATE") <= F.lit(target_end_date))
        )
    )

    # Left join to find:
    #   - missing dates (NO row in FEAT)
    #   - tail dates we want to rerun
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

    to_run_rows = (
        joined.filter(
            (F.col("HAS_FEATURE_DATE").is_null()) |
            (F.col("FEATURE_DATE") >= F.lit(rerun_start_date))
        )
        .select("FEATURE_DATE")
        .sort("FEATURE_DATE")
        .collect()
    )

    return [r["FEATURE_DATE"] for r in to_run_rows]


# =====================================================================
# FILE: src/your_project_name/features/feature_writer.py
# =====================================================================

from datetime import date

from snowflake.snowpark import Session, DataFrame
from snowflake.snowpark import functions as F


def delete_feature_date(session: Session, feature_table: str, feature_date: date):
    """
    Delete all rows from `feature_table` for a single feature_date.
    Makes per-day writes idempotent when paired with an INSERT.
    """
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
    Idempotent per-day write helper: DELETE + INSERT.

    - If skip_if_empty is True and features_df.count() == 0, does nothing.
    - Otherwise:
        * DELETE existing rows for feature_date
        * INSERT new rows from features_df
    """
    if skip_if_empty and features_df.count() == 0:
        return

    delete_feature_date(session, feature_table, feature_date)

    features_df.write.mode("append").save_as_table(feature_table)


# =====================================================================
# FILE: src/your_project_name/features/ohe.py
# =====================================================================

"""
Model-side One-Hot Encoding helpers.

This file is for pandas / numpy / sklearn code, not Snowpark.
Think: building ColumnTransformers, fitting encoders, etc.
"""

from typing import Sequence, Dict, Any

import pandas as pd
from sklearn.preprocessing import OneHotEncoder


def build_ohe_encoder(
    categorical_cols: Sequence[str],
    categories: Dict[str, Sequence[Any]] | None = None,
    handle_unknown: str = "ignore",
    sparse: bool = False,
) -> OneHotEncoder:
    """
    Build a configured OneHotEncoder for model dev / scoring.

    - `categories` can be a dict mapping column -> explicit category list
      (handy for regulatory / FED requirements where categories must be fixed).
    """
    if categories is not None:
        categories_list = [categories[col] for col in categorical_cols]
    else:
        categories_list = "auto"

    encoder = OneHotEncoder(
        categories=categories_list,
        handle_unknown=handle_unknown,
        sparse_output=sparse,
    )
    return encoder


def apply_ohe(
    df: pd.DataFrame,
    encoder: OneHotEncoder,
    categorical_cols: Sequence[str],
) -> pd.DataFrame:
    """
    Simple helper to transform categorical columns using a fitted encoder
    and return a new DataFrame with OHE columns.
    """
    ohe_array = encoder.transform(df[categorical_cols])
    ohe_df = pd.DataFrame(
        ohe_array,
        index=df.index,
        columns=encoder.get_feature_names_out(categorical_cols),
    )
    return pd.concat([df.drop(columns=categorical_cols), ohe_df], axis=1)


# =====================================================================
# FILE: src/your_project_name/features/masking.py
# =====================================================================

"""
Shared masking / conditional feature logic for model dev.

For example: masking certain hit types, replacing values with NaN based on
business rules, or applying conditional transformations before feeding into
a model pipeline.
"""

import pandas as pd
import numpy as np
from typing import Iterable


def apply_conditional_mask(
    df: pd.DataFrame,
    cols: Iterable[str],
    condition_series: pd.Series,
    replacement=np.nan,
) -> pd.DataFrame:
    """
    Apply a conditional mask to one or more columns:

        if condition_series is True -> replace value with `replacement`
    """
    df = df.copy()
    for col in cols:
        df.loc[condition_series, col] = replacement
    return df


# =====================================================================
# FILE: src/your_project_name/features/source_system/__init__.py
# =====================================================================

"""
Source-system-level feature helpers.

This package holds logic for mapping raw source tables (SQL Server, Oracle,
Snowflake raw ingest tables, etc.) into clean "rawish" DataFrames that your
domain-specific feature modules can use.

Examples:
  - build_corebank_deposit_df(...)
  - normalize_merchant_names(...)
"""


# =====================================================================
# FILE: src/your_project_name/features/source_system/transformations.py
# =====================================================================

"""
Source-system-level transformations.

These functions should:

  - Accept Snowpark or Spark DataFrames from upstream tables.
  - Perform basic cleaning and normalization by source system.
  - Return "rawish" DataFrames used by domain features (e.g., deposits).
"""

from snowflake.snowpark import Session, DataFrame
from snowflake.snowpark import functions as F


def build_raw_deposit_df_for_date(
    session: Session,
    population_table: str,
    txn_table: str,
    feature_date,
    lookback_days: int = 30,
) -> DataFrame:
    """
    Example helper that constructs a raw deposit DataFrame for a single feature_date
    using generic population + transaction tables.

    This is a good place to centralize per-source-system quirks:
      - column renaming
      - basic filters
      - schema normalization
    """
    pop_df = (
        session.table(population_table)
        .filter(
            (F.col("POPULATION_DATE") == F.lit(feature_date)) &
            (F.col("IS_ACTIVE") == F.lit(True))
        )
        .select("POPULATION_DATE", "ACCOUNT_ID")
    )

    txn_df = (
        session.table(txn_table)
        .filter(
            (F.col("POST_DATE") <= F.lit(feature_date)) &
            (F.col("POST_DATE") > F.dateadd("day", -lookback_days, F.lit(feature_date)))
        )
        .select("ACCOUNT_ID", "POST_DATE", "DEPOSIT_AMOUNT")
    )

    return pop_df.join(txn_df, on="ACCOUNT_ID", how="left")


# =====================================================================
# FILE: src/your_project_name/features/source_system/expressions.py
# =====================================================================

"""
Source-system-level column expressions.

Put low-level Snowpark expressions here that are specific to how a source
system encodes data (e.g., parsing raw codes into standardized flags).
"""

from snowflake.snowpark import DataFrame
from snowflake.snowpark import functions as F


def normalize_amount(df: DataFrame, col_name: str):
    """
    Example expression: ensure a numeric amount column is consistently typed.
    """
    return F.col(col_name).cast("NUMBER(18,2)")


# =====================================================================
# FILE: src/your_project_name/features/deposit/__init__.py
# =====================================================================

"""
Deposit-domain feature logic.

This package sits *above* source_system/ and focuses on:

  - combining source_system "rawish" data for deposits
  - computing business-facing deposit features
  - using expressions defined in deposit/expressions.py
"""


# =====================================================================
# FILE: src/your_project_name/features/deposit/transformations.py
# =====================================================================

"""
Deposit-level transformations.

These functions sit in the middle:

  - Take raw DataFrames from features.source_system.transformations
  - Apply deposit-specific feature expressions
  - Return feature DataFrames ready to be written to the feature store
    or converted to pandas for model dev.
"""

from snowflake.snowpark import DataFrame
from snowflake.snowpark import functions as F

from your_project_name.features.deposit import expressions as expr


def build_deposit_features_df(raw_df: DataFrame) -> DataFrame:
    """
    Apply deposit-domain feature expressions to a raw Snowpark DataFrame.
    """
    return raw_df.select(
        F.col("POPULATION_DATE").alias("FEATURE_DATE"),
        F.col("ACCOUNT_ID"),
        # Example features – replace with real ones:
        expr.num_deposits_30d(raw_df).alias("num_deposits_30d"),
        expr.total_deposit_amount_30d(raw_df).alias("total_deposit_amount_30d"),
    )


# =====================================================================
# FILE: src/your_project_name/features/deposit/expressions.py
# =====================================================================

"""
Deposit-domain feature expressions.

Each function returns a Snowpark Column. These are combined in
deposit/transformations.py.
"""

from snowflake.snowpark import DataFrame
from snowflake.snowpark import functions as F


def num_deposits_30d(df: DataFrame):
    return F.count("*")


def total_deposit_amount_30d(df: DataFrame):
    return F.sum("DEPOSIT_AMOUNT")


# =====================================================================
# FILE: src/your_project_name/config/__init__.py
# =====================================================================

import yaml
from pathlib import Path

def load_config(filename: str):
    """
    Simple YAML loader from src/your_project_name/config/.
    """
    path = Path(__file__).parent / filename
    with open(path, "r") as f:
        return yaml.safe_load(f)


# =====================================================================
# FILE: src/your_project_name/config/features_store.yaml
# (YAML content – put this in an actual YAML file, not Python)
# =====================================================================

"""
features:
  deposit:
    earliest_feature_date: "2020-01-01"
    max_daily_lag_days: 1
    rerun_last_n_days: 0
"""


# =====================================================================
# FILE: jobs/features/snowflake/write_deposit_features_production.py
# =====================================================================

"""
Snowpark job to build the historical deposit feature store in Snowflake.

Wires together:
  - config.features_store.yaml
  - features.date_logic.get_feature_dates_to_run
  - features.source_system.transformations.build_raw_deposit_df_for_date
  - features.deposit.transformations.build_deposit_features_df
  - features.feature_writer.write_feature_date
"""

from datetime import date
from typing import Optional

from snowflake.snowpark import Session

from your_project_name.config import load_config
from your_project_name.features.date_logic import get_feature_dates_to_run
from your_project_name.features.feature_writer import write_feature_date
from your_project_name.features.source_system.transformations import (
    build_raw_deposit_df_for_date,
)
from your_project_name.features.deposit.transformations import (
    build_deposit_features_df,
)

POP_TABLE = "POP_ACTIVE_ACCOUNTS_DAILY"
TXN_TABLE = "DEPOSIT_TRANSACTIONS"
FEATURE_TABLE = "FEAT_DEPOSIT_DAILY"


def write_deposit_features_for_date(session: Session, feature_date: date):
    raw_df = build_raw_deposit_df_for_date(
        session=session,
        population_table=POP_TABLE,
        txn_table=TXN_TABLE,
        feature_date=feature_date,
        lookback_days=30,
    )
    features_df = build_deposit_features_df(raw_df)
    write_feature_date(session, FEATURE_TABLE, features_df, feature_date)


def run_deposit_feature_job(
    session: Session,
    target_end_date_str: Optional[str] = None,
) -> str:
    """
    Stored procedure entrypoint.

    Example Snowflake DDL:

        CREATE OR REPLACE PROCEDURE RUN_DEPOSIT_FEATURE_JOB()
        RETURNS STRING
        LANGUAGE PYTHON
        RUNTIME_VERSION = '3.10'
        PACKAGES = ('snowflake-snowpark-python')
        HANDLER = 'write_deposit_features_production.run_deposit_feature_job';
    """

    cfg = load_config("features_store.yaml")["features"]["deposit"]

    earliest_date = date.fromisoformat(cfg["earliest_feature_date"])

    # Note: target_end_date_str is optional; you can add a branch to override if you want.
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
