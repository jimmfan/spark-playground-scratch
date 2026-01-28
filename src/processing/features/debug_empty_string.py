import numpy as np
from scipy import sparse

print("type(X_train):", type(X_train))

if sparse.issparse(X_train):
    print("X_train is sparse with dtype:", X_train.dtype)
    X_array = X_train.toarray()
else:
    print("X_train dtype:", getattr(X_train, "dtype", "no dtype attr"))
    X_array = np.asarray(X_train)

print("X_array dtype:", X_array.dtype)

import pandas as pd

# Get feature names from the preprocessor if available
try:
    feature_names = preprocessor.get_feature_names_out()
except AttributeError:
    # Fallback if get_feature_names_out isn't implemented
    feature_names = [f"col_{i}" for i in range(X_array.shape[1])]

X_pre_df = pd.DataFrame(X_array, columns=feature_names)

print("Preprocessed dtypes:")
print(X_pre_df.dtypes.value_counts())

print("\nColumns that are not numeric dtypes in preprocessed data:")
non_num_pre = X_pre_df.select_dtypes(exclude=[np.number]).columns.tolist()
print(non_num_pre)


# True where the value is actually a Python str
str_mask = X_pre_df.applymap(lambda v: isinstance(v, str))

# Which columns have any strings?
bad_cols = str_mask.any(axis=0)
print("\nColumns that contain at least one string value:")
print(X_pre_df.columns[bad_cols].tolist())

# Which rows have any strings?
bad_rows = str_mask.any(axis=1)
print("\nNumber of rows that contain at least one string value:", bad_rows.sum())

# Show a small sample of the offending cells
print("\nSample of offending values (strings) in the preprocessed matrix:")
print(X_pre_df.loc[bad_rows, bad_cols].head())
