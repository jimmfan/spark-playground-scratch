from impala.dbapi import connect

# Connect to the Impala daemon
conn = connect(host='your_impala_host', port=21050)  # Replace with your Impala host and port
cursor = conn.cursor()

# Set the memory limit for the session
cursor.execute("SET MEM_LIMIT = '6g';")

# List of tables to compute stats for
tables = ['table1', 'table2', 'table3']  # Replace with your table names

# Compute statistics for each table
for table in tables:
    compute_stats_query = f"COMPUTE STATS {table};"
    cursor.execute(compute_stats_query)
    print(f"Computed stats for table: {table}")

# Close the cursor and connection after all operations are done
cursor.close()
conn.close()

print("COMPUTE STATS command executed for all tables.")
