import numpy as np

# Assume arr1 and arr2 are your numpy arrays

# 1. Boolean mask of mismatches
mask = arr1 != arr2

# 2. Indices of mismatches
diff_idx = np.where(mask)

# 3. Print mismatching positions and their values (works for any dimensionality)
print("Number of mismatches:", len(diff_idx[0]))
for idx in zip(*diff_idx):
    print("Index:", idx, "arr1:", arr1[idx], "arr2:", arr2[idx])

# 4. (Optional) If you want tolerance-based matching for floats:
# tol_mask = ~np.isclose(arr1, arr2, rtol=1e-6, atol=1e-8)
# tol_diff_idx = np.where(tol_mask)
# for idx in zip(*tol_diff_idx):
#     print("Index:", idx, "arr1:", arr1[idx], "arr2:", arr2[idx])
