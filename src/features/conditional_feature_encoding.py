import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
import xgboost as xgb

# ---- 1) Masker that takes [cat, hist_flag] -> [cat_or_nan]
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class MaskCategoricalToNaN(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=object)  # (n, 2): [categorical, hist_flag]
        cat  = X[:, [0]].copy()
        mask = X[:, 1].astype(float).reshape(-1, 1)
        cat[mask[:, 0] == 1] = np.nan
        return cat  # shape (n, 1)

    # ✅ add this for sklearn 1.0.2 compatibility
    def get_feature_names_out(self, input_features=None):
        # input_features will be like ['cat_feature1', 'hist_flag'] for this branch
        if input_features is None or len(input_features) == 0:
            return np.array(["masked_cat"], dtype=object)
        # name the output after the first (categorical) input
        return np.array([input_features[0]], dtype=object)


def build_ohe_with_mask(cat_name, categories, hist_flag_col):
    """Takes raw cat + hist_flag, masks to NaN, then OHE with fixed vocab."""
    return (
        cat_name,
        Pipeline(steps=[
            ("mask", MaskCategoricalToNaN()),
            ("ohe", OneHotEncoder(
                categories=[categories],
                handle_unknown="ignore",
                sparse_output=False,  # or True if you prefer
            )),
        ]),
        [cat_name, hist_flag_col],  # feed both columns into this branch
    )

# ---- 2) Wire your preprocessor
# ohe_dict: {"cat_feature1": [...], "cat_feature2": [...]}
preprocessor = ColumnTransformer(
    transformers=[
        build_ohe_with_mask("cat_feature1", ohe_dict["cat_feature1"], "hist_flag"),
        build_ohe_with_mask("cat_feature2", ohe_dict["cat_feature2"], "hist_flag"),
        # ("nums", "passthrough", numeric_cols),
    ],
    remainder="drop",
)

pipeline_template = Pipeline([
    ("prep", preprocessor),
    ("model", xgb.XGBClassifier(random_state=42, n_jobs=-1)),
])
