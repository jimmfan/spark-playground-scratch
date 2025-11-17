from sklearn.preprocessing import OneHotEncoder

def make_ohe(categories, sparse=False):
    """Return a configured OneHotEncoder."""
    return OneHotEncoder(
        categories=[categories],
        handle_unknown="ignore",   # fix the old typo
        sparse=sparse,             # sklearn 1.0.2
    )

from sklearn.pipeline import Pipeline

def build_ohe_pipeline(column_name, categories, sparse=False):
    """
    ColumnTransformer branch for a simple OHE on one categorical column.
    Returns (name, estimator, columns).
    """
    ohe_pipe = Pipeline(steps=[
        ("ohe", make_ohe(categories, sparse=sparse)),
    ])
    return (
        f"ohe_{column_name}",  # name used inside ColumnTransformer
        ohe_pipe,              # estimator
        [column_name],         # input column list
    )

class MaskCategoricalToNaN(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=object)  # (n, 2): [categorical, hit_type]
        cat = X[:, [0]].copy()
        mask_vals = pd.to_numeric(X[:, 1], errors="coerce")
        mask = np.isin(mask_vals, [1, 2]).reshape(-1, 1)
        cat[mask[:, 0]] = np.nan
        return cat

    def get_feature_names_out(self, input_features=None):
        if input_features is None or len(input_features) == 0:
            return np.array(["masked_cat"], dtype=object)
        return np.array([input_features[0]], dtype=object)


def build_ohe_with_mask(cat_name, categories, hit_type_col, sparse=False):
    """
    ColumnTransformer branch for [cat_name, hit_type_col] -> mask -> OHE.
    """
    masked_ohe_pipe = Pipeline(steps=[
        ("mask", MaskCategoricalToNaN()),
        ("ohe", make_ohe(categories, sparse=sparse)),
    ])
    return (
        f"ohe_{cat_name}",          # name inside ColumnTransformer
        masked_ohe_pipe,            # estimator
        [cat_name, hit_type_col],   # input columns
    )

preprocessor = ColumnTransformer(
    transformers=[
        build_ohe_with_mask("cat_feature1", ohe_dict["cat_feature1"], "hit_type", sparse=False),
        build_ohe_with_mask("cat_feature2", ohe_dict["cat_feature2"], "hit_type", sparse=False),
        # plus passthrough / other transformers
    ],
    remainder="passthrough",
)



## Updated version:

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

class MaskCategoricalToNaN(BaseEstimator, TransformerMixin):
    def __init__(self, mask_values):
        # important: store raw arg exactly as passed for sklearn
        self.mask_values = mask_values

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=object)  # (n, 2): [categorical, hit_type]
        cat = X[:, [0]].copy()
        mask_vals = pd.to_numeric(X[:, 1], errors="coerce")
        mask = np.isin(mask_vals, list(self.mask_values)).reshape(-1, 1)
        cat[mask[:, 0]] = np.nan
        return cat  # (n, 1)

    def get_feature_names_out(self, input_features=None):
        if input_features is None or len(input_features) == 0:
            return np.array(["masked_cat"], dtype=object)
        return np.array([input_features[0]], dtype=object)

def build_ohe_with_mask(cat_name, categories, hit_type_col, mask_values):
    pipe = Pipeline([
        ("mask", MaskCategoricalToNaN(mask_values=mask_values)),
        ("ohe", OneHotEncoder(
            categories=[categories],
            handle_unknown="ignore",
            sparse=False,   # sklearn 1.0.2 style
        )),
    ])
    return (
        f"ohe_{cat_name}",
        pipe,
        [cat_name, hit_type_col],
    )

ohe_dict = {
    "cat_feature1": ["A", "B", "C"],
    "cat_feature2": ["X", "Y"],
}

numeric_cols = ["age", "balance"]

preprocessor = ColumnTransformer(
    transformers=[
        build_ohe_with_mask("cat_feature1", ohe_dict["cat_feature1"], "hit_type", mask_values=[1, 2]),
        build_ohe_with_mask("cat_feature2", ohe_dict["cat_feature2"], "hit_type", mask_values=[1, 2]),
        ("keep_numeric", "passthrough", numeric_cols),
    ],
    remainder="drop",
)

df = pd.DataFrame({
    "cat_feature1": ["A", "B", "C", "A", "B"],
    "cat_feature2": ["X", "Y", "X", "Y", "X"],
    "hit_type":     [0,   1,   2,   0,   2],   # rows 1,2,4 should be masked
    "age":          [40,  51,  33,  60,  45],
    "balance":      [1000, 2000, 1500, 500, 2500],
})

X_prepared = preprocessor.fit_transform(df)
feature_names = preprocessor.get_feature_names_out()

print("Feature names:", feature_names)
print(pd.DataFrame(X_prepared, columns=feature_names))
