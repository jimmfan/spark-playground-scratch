from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

class GroupStandardScaler(BaseEstimator, TransformerMixin):
    """
    Apply StandardScaler separately within each group (e.g. consumer vs business).
    """
    def __init__(self, group_col):
        self.group_col = group_col
        self.scalers_ = {}

    def fit(self, X, y=None):
        df = pd.DataFrame(X).copy()
        self.numeric_cols_ = df.select_dtypes(include=[np.number]).columns.tolist()
        for grp, grp_df in df.groupby(self.group_col):
            scaler = StandardScaler().fit(grp_df[self.numeric_cols_])
            self.scalers_[grp] = scaler
        return self

    def transform(self, X):
        df = pd.DataFrame(X).copy()
        for grp, scaler in self.scalers_.items():
            mask = df[self.group_col] == grp
            df.loc[mask, self.numeric_cols_] = scaler.transform(df.loc[mask, self.numeric_cols_])
        return df

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

numeric_cols = ["deposit_amount", "deposit_count", "account_age"]
cat_cols = ["region", "industry"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", GroupStandardScaler(group_col="account_type"), numeric_cols + ["account_type"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ]
)

model = Pipeline(steps=[
    ("preprocess", preprocessor),
    ("xgb", xgb.XGBClassifier(...))
])