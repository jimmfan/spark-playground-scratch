import numpy as np
import pandas as pd
from typing import Iterable, Sequence, Union

def apply_mask(
    df: pd.DataFrame,
    cat_cols: Sequence[str],
    hit_type_col: str = "hit_type",
    keep_values: Iterable[Union[int, float, str]] = (1, 2),
    inplace: bool = False,
) -> pd.DataFrame:
    """
    Mask realtime categorical features based on hit_type.

    Rules:
      - If hit_type is in keep_values → KEEP categorical values
      - If hit_type is NOT in keep_values (or is NaN/invalid) → set those
        categorical columns to NaN.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe. Must contain `hit_type_col` and all `cat_cols`.
    cat_cols : list of str
        Categorical/realtime feature columns to mask.
    hit_type_col : str, default "hit_type"
        Column indicating which rows should keep their realtime features.
    keep_values : iterable of int/float/str, default (1, 2)
        Values of hit_type that should KEEP their categorical values.
        Everything else gets masked to NaN.
    inplace : bool, default False
        If True, modify `df` in place and return it.
        If False, work on a copy and return the copy.

    Returns
    -------
    pd.DataFrame
        DataFrame with the same columns as input, but with `cat_cols`
        masked to NaN where hit_type_col NOT in keep_values.
    """
    if not inplace:
        df = df.copy()

    # normalize hit_type to float so it works with 1, 1.0, "1", "1.0", etc.
    hit_vals = pd.to_numeric(df[hit_type_col], errors="coerce").astype(float)

    # normalize keep_values to float as well
    keep_vals_arr = np.array(list(keep_values), dtype=float)

    # True where we want to KEEP the categorical values
    keep_mask = np.isin(hit_vals.values, keep_vals_arr)

    # rows we want to MASK (hit_type not in keep_values OR hit_type is NaN)
    mask_rows = ~keep_mask

    # apply masking to all requested categorical columns
    if mask_rows.any():
        df.loc[mask_rows, list(cat_cols)] = np.nan

    return df
