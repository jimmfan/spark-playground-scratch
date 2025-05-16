🔍 What Happened with the Table and Duplicates
We copied data into a Hive table folder using distcp, which moved raw Parquet partition folders to HDFS, RECOVER PARTITIONS — this successfully registered the partition folders with Hive’s metastore.

However, the first time our Spark job ran:

```python
df.write \
  .format("hive") \
  .mode("append") \
  .partitionBy("event_date") \
  .option("path", "hdfs:/.../your_table") \
  .saveAsTable("database.table")
```

it either created or redefined the Hive table, but didn’t correctly preserve event_date as a partition column.
As a result:

Spark wrote .parquet files into the root folder of the table

It also created a partition folder like event_date=2025-04-01, but both now exist with overlapping data

Later Spark jobs, using the same .partitionBy("event_date"), began writing correctly into partition folders like:

```bash
/your_table/event_date=2025-04-01/
```

But now we have duplicate records:

One copy in the root folder

Another copy in the correct partition folder

We confirmed this by running:

```sql
DESCRIBE FORMATTED database.table PARTITION (event_date = '2025-04-01')
```

which showed both the root table path and the partition path — confirming Spark is scanning both.

### What Is the Hive Metastore and Why It Matters
The Hive Metastore is a catalog that tracks:

Table schema

Data formats and paths

Partition columns and values

When a partition like event_date=2025-04-01 is registered in the metastore, Hive and Spark can efficiently scan only that folder.
But if data also exists in the root of the table, Spark still scans it — even if a partition filter is used — because root files are treated as "unpartitioned" and Spark needs to check whether any rows match.

This is why we're seeing duplicates even when filtering on event_date.

### What’s the Difference Between Spark and Hive?
Hive is a data warehouse layer built on top of Hadoop. It stores metadata in the Hive Metastore and uses that to organize and query data in tables and partitions (even if the data lives in HDFS).

Spark is a fast, general-purpose data processing engine. It can interact with Hive tables, but it also has its own logic for writing data — and doesn’t always rely on the Hive Metastore unless explicitly told to.

So when we write data using Spark (like .saveAsTable()), we’re trusting Spark to either:

Use Hive’s existing metadata (if everything lines up)

Or define a new table — which can overwrite or conflict with Hive’s existing schema

✅ What This Means
Spark and Hive both scan root and partition folders during queries

That’s why we're seeing duplicate rows — especially for early data before the table was properly written with partition awareness

Even if we filter by event_date, Spark reads the root files just in case

