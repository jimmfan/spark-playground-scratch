# # Directory structure:
# # ├── config
# # │   └── pipeline.yaml
# # ├── src
# # │   └── pipeline_runner.py
# # └── requirements.txt

# # File: config/pipeline.yaml
# pipeline:
#   name: customer_transform
#   source:
#     table: raw.customers
#     filter: "country = 'US' AND status = 'active'"
#   target:
#     table: curated.customers_cleaned
#     mode: overwrite
#   columns:
#     - name: customer_id
#       type: string
#       nullable: false
#     - name: full_name
#       type: string
#       transform: "concat_ws(' ', first_name, last_name)"
#     - name: age
#       type: int
#       transform: "datediff(current_date(), birth_date) // 365"
#     - name: signup_date
#       type: date
#       nullable: true

# File: src/pipeline_runner.py
import yaml
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("YamlDrivenPipeline").getOrCreate()

with open("config/pipeline.yaml") as f:
    cfg = yaml.safe_load(f)

pipeline = cfg["pipeline"]
df = spark.table(pipeline["source"]["table"])

if "filter" in pipeline["source"]:
    df = df.filter(pipeline["source"]["filter"])

select_exprs = []
for col in pipeline["columns"]:
    if "transform" in col:
        expr = F.expr(col["transform"]).alias(col["name"])
    else:
        expr = F.col(col["name"])
    select_exprs.append(expr)

df = df.select(*select_exprs)

df.write.mode(pipeline["target"]["mode"]).saveAsTable(pipeline["target"]["table"])

# File: requirements.txt
pyyaml
pyspark
