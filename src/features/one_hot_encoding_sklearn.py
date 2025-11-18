from sklearn.preprocessing import OneHotEncoder 
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import xgboost as xgb

def build_ohe_pipeline(column_name, categories, fill_value=0): 
    ohe_pipeline = Pipeline(
        steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value=fill_value)),
            (
                "ohe",
                OneHotEncoder(
                    categories=[categories], 
                    handle_unknown="ignore", 
                    sparse=False # sparse_output=False for sklearn 1.2+
            ),
        )]
    )
    return (column_name, ohe_pipeline, [column_name])


passthrough_features = ["num_feature1", "num_feature2"]

ohe_dict = {
    "cat_feature1": ["A", "B", "C"],
    "cat_feature2": ["X", "Y"],
}

preprocessor = ColumnTransformer(
    transformers=[
        build_ohe_pipeline("cat_feature1", ohe_dict['cat_feature1'], fill_value=0),
        build_ohe_pipeline("cat_feature2", ohe_dict['cat_feature2'], fill_value=0),
        ("pass", "passthrough", passthrough_features)
    ],
    remainder="drop", 
)

model_template = xgb.XGBClassifier(
    random_state=42, n_jobs=-1,
)

pipeline_template = Pipeline([
    ("prep", preprocessor), ("model", model_template),
])