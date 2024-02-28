from pyspark.sql import SparkSession
import yaml

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Schema to YAML") \
    .enableHiveSupport() \
    .getOrCreate()

# Replace with your schema name
schema_name = 'default'
tables_df = spark.sql(f"SHOW TABLES IN {schema_name}")

# Initialize structure for YAML
tables_info = {'tables': []}

for row in tables_df.collect():
    table_name = row.tableName
    # Getting extended table information for partition and column details
    extended_info = spark.sql(f"DESCRIBE FORMATTED {schema_name}.{table_name}").collect()
    
    # Parse the extended information to extract fields and partitions
    fields = []
    partitions = []
    in_partition_section = False
    for info in extended_info:
        if info.col_name == '# Partition Information':
            in_partition_section = True
        elif info.col_name == '' or info.col_name.startswith('#'):
            in_partition_section = False
        elif in_partition_section:
            partitions.append({'name': info.col_name.strip(), 'type': info.data_type.strip()})
        else:
            fields.append({'name': info.col_name.strip(), 'type': info.data_type.strip()})
    
    # Append table info
    tables_info['tables'].append({
        'name': table_name,
        'database': schema_name,
        'partitions': partitions,
        'fields': fields
    })

# Convert to YAML
yaml_str = yaml.dump(tables_info, sort_keys=False)

# Save to YAML file
with open('tables_schema.yml', 'w') as file:
    file.write(yaml_str)

print("YAML file 'tables_schema.yml' has been created.")
