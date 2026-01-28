from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression

# Suppose we have:
# - "gender": fill missing with "unknown"
# - "state": fill missing with "NA"
# - numeric columns: fill with median

categorical_cols = ["gender", "state"]
numeric_cols = ["age", "income"]

# Pipelines for each column
gender_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

state_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="constant", fill_value="NA")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

numeric_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median"))
])

# ColumnTransformer ties everything together
preprocessor = ColumnTransformer(
    transformers=[
        ("gender", gender_pipeline, ["gender"]),
        ("state", state_pipeline, ["state"]),
        ("num", numeric_pipeline, numeric_cols),
    ]
)

# Final model
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression())
])

model.fit(X_train, y_train)
