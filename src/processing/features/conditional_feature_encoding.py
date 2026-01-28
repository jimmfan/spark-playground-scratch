import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# ---- 1) Masker that takes [categorical, hit_type] -> [categorical_or_nan]
class MaskCategoricalToNaN(BaseEstimator, TransformerMixin):
    """
    Blanks out the categorical value when hit_type ∈ {1, 2}.
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=object)  # (n, 2): [categorical, hit_type]
        cat = X[:, [0]].copy()
        # convert hit_type to float or string-safe numeric
        mask_vals = pd.to_numeric(X[:, 1], errors="coerce")
        mask = np.isin(mask_vals, [1, 2]).reshape(-1, 1)
        cat[mask[:, 0]] = np.nan  # blank out when hit_type==1 or 2
        return cat  # shape (n, 1)

    # Required for sklearn <1.1 when using get_feature_names_out
    def get_feature_names_out(self, input_features=None):
        if input_features is None or len(input_features) == 0:
            return np.array(["masked_cat"], dtype=object)
        return np.array([input_features[0]], dtype=object)


def build_ohe_with_mask(cat_name, categories, hit_type_col):
    """Takes [cat_name, hit_type_col] -> masked -> OHE"""
    return (
        f"ohe_{cat_name}",
        Pipeline(steps=[
            ("mask", MaskCategoricalToNaN()),
            ("ohe", OneHotEncoder(
                categories=[categories],
                handle_unknown="ignore",
                sparse=False,   # for sklearn 1.0.2
            )),
        ]),
        [cat_name, hit_type_col],
    )

# ---- 2) Example feature setup
ohe_dict = {
    "cat_feature1": ["A", "B", "C"],
    "cat_feature2": ["X", "Y"],
}
numeric_cols = ["age", "balance"]

preprocessor = ColumnTransformer(
    transformers=[
        build_ohe_with_mask("cat_feature1", ohe_dict["cat_feature1"], "hit_type"),
        build_ohe_with_mask("cat_feature2", ohe_dict["cat_feature2"], "hit_type"),
        ("numeric_passthrough", "passthrough", numeric_cols),
    ],
    remainder="passthrough",  # keep any extras for now
)

# ---- 3) Tiny sample data for testing
df = pd.DataFrame({
    "cat_feature1": ["A", "B", "C", "A", "B"],
    "cat_feature2": ["X", "Y", "X", "Y", "X"],
    "hit_type":     [0, 1, 2, 0, 2],   # blank out cat features when 1 or 2
    "age":          [40, 51, 33, 60, 45],
    "balance":      [1000, 2000, 1500, 500, 2500],
    "extra_raw":    [7.5, 8.1, 9.0, 7.9, 8.4],
})

# ---- 4) Fit + transform (sanity check)
Z = preprocessor.fit_transform(df)
names = preprocessor.get_feature_names_out()

print("Transformed shape:", Z.shape)
print("First 10 feature names:", names[:10])

# Inspect the output
out_df = pd.DataFrame(Z, columns=names)
print(out_df)

# ---- 5) Optional sanity assertions
ohe1 = preprocessor.named_transformers_["ohe_cat_feature1"].named_steps["ohe"]
ohe2 = preprocessor.named_transformers_["ohe_cat_feature2"].named_steps["ohe"]

k1 = len(ohe1.get_feature_names_out(["cat_feature1"]))
k2 = len(ohe2.get_feature_names_out(["cat_feature2"]))

start1, end1 = 0, k1
start2, end2 = end1, end1 + k2

mask_rows = df["hit_type"].isin([1, 2]).values
assert np.all(Z[mask_rows, start1:end1] == 0), "cat_feature1 masking failed"
assert np.all(Z[mask_rows, start2:end2] == 0), "cat_feature2 masking failed"

print("\n✅ Sanity check passed: hit_type 1/2 rows were blanked correctly.")

