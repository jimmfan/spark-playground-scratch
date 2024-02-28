from pyspark.sql import SparkSession
import yaml

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Schema to YAML with Metadata") \
    .enableHiveSupport() \
    .getOrCreate()

# Replace with your schema name
schema_name = 'default'
tables_df = spark.sql(f"SHOW TABLES IN {schema_name}")

# Initialize structure for YAML
tables_info = {'tables': []}

for row in tables_df.collect():
    table_name = row.tableName
    # Getting extended table information for partition, column details, and other metadata
    extended_info = spark.sql(f"DESCRIBE FORMATTED {schema_name}.{table_name}").collect()
    
    # Initialize dictionary to hold table metadata and details
    table_dict = {
        'name': table_name,
        'database': schema_name,
        'partitions': [],
        'fields': [],
    }

    # Flags to identify where in the metadata we are
    in_partition_section = False
    in_column_section = True  # Assuming columns come first in DESCRIBE FORMATTED output

    for info in extended_info:
        col_name = info.col_name.strip()
        if col_name == 'Partition Information':
            in_partition_section = True
            in_column_section = False
        elif col_name == 'Detailed Table Information':
            in_partition_section = False
            in_column_section = False
        elif col_name == '' or col_name.startswith('#'):
            continue
        elif in_partition_section:
            table_dict['partitions'].append({'name': col_name, 'type': info.data_type.strip()})
        elif in_column_section:
            table_dict['fields'].append({'name': col_name, 'type': info.data_type.strip()})
        else:  # Capture table-level metadata
            # Splitting on ':', maxsplit=1 to handle cases where ':' appears in the value
            key_value = col_name.split(':', 1)
            if len(key_value) == 2:
                key, value = key_value
                # Assuming metadata keys are unique, directly add them to the table_dict
                table_dict[key.strip().replace(' ', '_').lower()] = value.strip()

    # Append table info with metadata to the list
    tables_info['tables'].append(table_dict)

# Convert to YAML
yaml_str = yaml.dump(tables_info, sort_keys=False, default_flow_style=False)

# Save to YAML file
with open('tables_schema_with_metadata.yml', 'w') as file:
    file.write(yaml_str)

print("YAML file 'tables_schema_with_metadata.yml' has been created.")
