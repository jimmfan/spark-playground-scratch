## Example: Validating Data Consistency Between Old and New PySpark Data Pipelines

### Context
The new data pipeline has been modified to stack the data into a JSON column and then flatten it to match the structure of the previous pipeline. To ensure that the new pipeline produces the same output as the old one, we performed a validation by comparing the datasets from both pipelines.

### Steps to Validate Data Consistency

1. **Extract Data from Both Pipelines**:
    - Extracted the final output datasets from both the previous and new pipelines.
    - For the new pipeline, the data was initially stacked into a JSON column and then flattened to match the previous pipeline's structure.

2. **Union Distinct Operation**:
    - Performed a `union distinct` operation on the two datasets to combine them into a single DataFrame, ensuring that only distinct records are retained.

    ```python
    # Read data from both pipelines
    old_pipeline_df = spark.read.parquet("path/to/old_pipeline/output")
    new_pipeline_df = spark.read.parquet("path/to/new_pipeline/output")

    # Flatten the new pipeline data if needed
    new_pipeline_df_flat = new_pipeline_df.selectExpr("json_column.*")

    # Perform union distinct
    combined_df = old_pipeline_df.union(new_pipeline_df_flat).distinct()
    ```

3. **Count Comparison**:
    - Counted the number of records in both the old and new pipeline outputs.
    - Counted the number of records in the combined DataFrame.

    ```python
    # Count records in both datasets
    old_count = old_pipeline_df.count()
    new_count = new_pipeline_df_flat.count()
    combined_count = combined_df.count()

    # Validation check
    assert old_count == new_count, "Record counts do not match between old and new pipeline outputs"
    assert combined_count == old_count, "Combined record count does not match the original count"
    ```

### Validation Results

- **Old Pipeline Record Count**: `500,000`
- **New Pipeline Record Count**: `500,000`
- **Combined DataFrame Record Count**: `500,000`

All record counts matched, indicating that the new data pipeline's output is consistent with the previous one.

### Conclusion

The validation process confirmed that the new PySpark data pipeline, which stacks data into a JSON column and flattens it, produces an output that is consistent with the previous pipeline. The `union distinct` operation and count comparison verified that no records were lost or duplicated in the process.

