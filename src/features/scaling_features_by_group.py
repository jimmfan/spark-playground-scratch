from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

class GroupStandardScaler(BaseEstimator, TransformerMixin):
    """
    Applies StandardScaler within each group (e.g. consumer vs business),
    and optionally drops the group column after scaling.
    """
    def __init__(self, group_col, drop_group_col=True):
        self.group_col = group_col
        self.drop_group_col = drop_group_col
        self.scalers_ = {}

    def fit(self, X, y=None):
        df = pd.DataFrame(X).copy()

        # Identify numeric columns (excluding the group_col)
        self.numeric_cols_ = [
            c for c in df.columns if c != self.group_col and np.issubdtype(df[c].dtype, np.number)
        ]

        # Fit one StandardScaler per group
        for grp, grp_df in df.groupby(self.group_col):
            scaler = StandardScaler().fit(grp_df[self.numeric_cols_])
            self.scalers_[grp] = scaler

        return self

    def transform(self, X):
        df = pd.DataFrame(X).copy()
        for grp, scaler in self.scalers_.items():
            mask = df[self.group_col] == grp
            df.loc[mask, self.numeric_cols_] = scaler.transform(df.loc[mask, self.numeric_cols_])

        if self.drop_group_col:
            df = df.drop(columns=[self.group_col])

        return df[self.numeric_cols_] if self.drop_group_col else df


from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
import xgboost as xgb

numeric_cols = ["deposit_amount", "deposit_count", "account_age"]
cat_cols = ["region", "industry"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", GroupStandardScaler(group_col="account_type", drop_group_col=True),
         numeric_cols + ["account_type"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ]
)

model = Pipeline([
    ("preprocess", preprocessor),
    ("xgb", xgb.XGBClassifier(
        max_depth=5,
        learning_rate=0.1,
        n_estimators=200,
        scale_pos_weight=300,  # since you have 0.31% event rate
        eval_metric="auc"
    )),
])
