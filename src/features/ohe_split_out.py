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
