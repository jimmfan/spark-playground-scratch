from impala.dbapi import connect
from impala.error import Error

def compute_stats_for_tables(tables):
    try:
        # Connect to the Impala daemon
        conn = connect(host='your_impala_host', port=21050)  # Replace with your Impala host and port
        cursor = conn.cursor()

        # Set the memory limit for the session
        cursor.execute("SET MEM_LIMIT = '6g';")

        # Loop through each table
        for table_name in tables:
            print(f"Processing table: {table_name}")

            # Retrieve the list of partitions for the current table
            cursor.execute(f"SHOW PARTITIONS {table_name};")
            partitions = cursor.fetchall()

            # Compute statistics for each partition
            for partition in partitions:
                # Extract the partition specification
                partition_spec = partition[0]  # Adjust based on the actual structure of the partition data
                compute_stats_query = f"COMPUTE INCREMENTAL STATS {table_name} PARTITION ({partition_spec});"
                cursor.execute(compute_stats_query)
                print(f"Computed stats for partition: {partition_spec} of table: {table_name}")

        print("COMPUTE STATS command executed for all tables and partitions.")
        
    except Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection after all operations are done
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# List of tables to compute stats for
tables = ['table1', 'table2', 'table3']  # Replace with your actual table names

# Compute stats for all specified tables
compute_stats_for_tables(tables)
