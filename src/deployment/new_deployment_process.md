+----------------------------+
| 1. SageMaker (Dev)         |
| -------------------------- |
| - Develop Python module    |
| - Test logic locally       |
+------------+----------------
             |
             |  Pushes code
             v
+----------------------------+
| 2. GitHub Repo             |
| -------------------------- |
| - Stores code              |
| - Triggers CI/CD           |
+------------+----------------
             |
             | GitHub Actions
             v
+----------------------------+
| 3. GitHub Actions CI       |
| -------------------------- |
| Purpose: Build + Package   |
| Runs: setup.py / pip       |
| Pushes artifact to:        |
| - Artifactory              |
+------------+----------------
             |
             | Publishes versioned artifact
             v
+----------------------------+
| 4. Artifactory             |
| -------------------------- |
| - Holds built Python pkg   |
| - Source for Harness       |
+------------+----------------
             |
             | Triggered by release
             v
+--------------------------------+
| 5. Harness CI/CD Runner        |
| ------------------------------ |
| Purpose: Deploy module         |
| Runs: main.py                  |
| Code: Deployment Logic         |
| - pip install from Artifactory |
| - Connects to Snowflake        |
| - CREATE PROC/TABLE/TASK       |
+------------+--------------------
             |
             | Registers into
             v
+-----------------------------+
| 6. Snowflake                |
| --------------------------- |
| Purpose: Run business logic |
| Runs: Stored Procedure      |
| Trigger: Scheduled Task     |
| Code: Python (Snowpark)     |
+-----------------------------+


### 📦 Deployment Flow: Step-by-Step Breakdown

| Step | Platform/Tool       | Purpose                                    | Runs What                             | When It Runs                    | Code Type         |
|------|---------------------|---------------------------------------------|----------------------------------------|----------------------------------|-------------------|
| 1    | **SageMaker**       | Develop and test business logic             | Python module (`run()` in sproc)       | During development               | Business logic    |
| 2    | **GitHub**          | Source code management                      | Git repo (your project code)           | On code commit or PR merge       | N/A               |
| 3    | **GitHub Actions**  | Build and publish the package               | `setup.py` / `build.sh` (pip package)  | On push to `main` or release tag | Build pipeline    |
| 4    | **Artifactory**     | Store versioned Python packages             | `your_project-x.y.z.tar.gz`            | Always available                 | N/A               |
| 5    | **Harness**         | Deploy module to Snowflake                  | `main.py` (registers Snowflake objects)| On deployment trigger            | Deployment logic  |
| 6    | **Snowflake**       | Execute business logic inside the platform  | Stored Procedure (`run()` function)    | On task schedule (e.g., cron)    | Business logic    |


Plain-English Description for Docs/Stakeholders
Data engineers write and test Python code in SageMaker, then push it to GitHub.

GitHub Actions takes that code, builds a versioned artifact, and pushes it to Artifactory.

Harness is triggered to install the module and run a deployment script that creates objects in Snowflake: tables, stored procedures, and scheduled tasks.

Finally, Snowflake runs those stored procedures on a schedule — no further involvement from Harness is needed after deployment.

