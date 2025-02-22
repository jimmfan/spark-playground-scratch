Summary of Changes
1. Transition to JSON Columns for Unique Attributes
Previous Approach:
Two data types with slightly different schemas were unioned together, requiring the creation of additional NULL columns to align the schemas.
This approach introduced redundancy and increased schema complexity.
Updated Approach:
Retained only the shared columns between the two data types in the primary schema.
Unique, type-specific columns were consolidated into a JSON column, allowing flexibility and preserving all attributes without altering the main schema.
Benefits:
Simplifies the schema by focusing on shared attributes.
Improves flexibility for future changes or additional data sources.
Reduces storage overhead and query complexity.
2. Introduction of Configuration via YAML Files
Previous Approach:
Configuration settings were hard-coded within the pipeline, requiring code changes for every configuration update.
This approach reduced maintainability and made the pipeline less adaptable to different environments or use cases.
Updated Approach:
Replaced hard-coded configurations with a YAML configuration file, centralizing all configurable parameters.
The YAML file now manages settings such as data source paths, transformation rules, and output locations.
Benefits:
Centralized configuration improves maintainability and reduces the risk of errors.
Facilitates environment-specific configurations (e.g., dev, staging, production).
Allows non-technical users or analysts to adjust parameters without modifying code.
 Enhanced Integration with Document Store

Previous Approach: The pipeline relied on a less flexible integration method for accessing the document store, which can cause problems in distributed environments.
Updated Approach: Improved the integration by packaging the necessary logic into the pipeline, ensuring consistency and reliability across all processing nodes.
Benefits: Increased flexibility, better scalability, and improved reliability when working with distributed data processing.
Improved flexibility by eliminating reliance on global variables.
Enhanced scalability and robustness of the pipeline by packaging dependencies directly into the UDF.
Simplifies maintenance and debugging in distributed environments.