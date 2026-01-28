# Spark Playground & Scratchpad

This repository is a collection of scripts, tools, and experiments involving PySpark, Python, and various data integrations. It serves as a playground for testing new libraries, debugging issues, and storing reusable code snippets.

## Project Structure

The repository is organized into the following categories:

### `src/`
- **`apps/`**: Interactive applications using Streamlit and Solara.
- **`common/`**: Shared utilities for date handling, logging, and general helper functions.
- **`devops/`**: Scripts and tools for deployment and infrastructure.
- **`integrations/`**: Connectors, examples, and utilities for external systems:
  - `snowflake`, `hdfs`, `filenet`, `sharepoint`, `artifactory`, `confluence`, etc.
- **`ml/`**: Machine Learning models, experiments, and tools:
  - `models`, `scikit_learn`, `onnx`, `optuna`, `model_monitoring`.
- **`processing/`**: Data processing, EDA, and feature engineering scripts:
  - `features`, `eda`, `pdf`, `xml`, `json_mapping`, `sql_parse`.
- **`spark/`**: PySpark-specific extensions, UDFs, and debugging tools.
- **`tools/`**: Meta-tools for code understanding, dependency mapping, and project organization.

### Other Directories
- **`config/`**: Configuration files (YAML).
- **`docs/`**: Documentation and templates.
- **`scripts/`**: Shell scripts for Git and GitHub operations.
- **`tests/`**: Unit tests and mock data.

## Getting Started

This project uses `poetry` for dependency management (implied by `pyproject.toml`), though many scripts are standalone.

To install dependencies (if applicable):
```bash
make setup
```

To run tests:
```bash
make test
```

## Usage

Most scripts in `src/` are designed to be run independently or imported as modules. Check individual directories for specific examples.
