import subprocess

# Example: delete one partition file
partition_file = "/warehouse/mydb/mytable/dt=2025-10-01/part-00012-abc.snappy.parquet"
subprocess.run(["hdfs", "dfs", "-rm", "-skipTrash", partition_file])
