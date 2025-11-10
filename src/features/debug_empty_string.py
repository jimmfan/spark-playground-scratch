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
