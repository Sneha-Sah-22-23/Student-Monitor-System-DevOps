from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, hour

spark = SparkSession.builder \
    .appName("Student Focus Monitor - Distraction Analysis") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

df = spark.read.csv("/app/data/distraction_log.csv", header=True, inferSchema=True)
df = df.withColumn("Timestamp", col("Timestamp").cast("timestamp"))
df = df.withColumn("Hour", hour(col("Timestamp")))

# 1. Hourly breakdown
hourly = df.groupBy("Hour", "Status").agg(count("*").alias("Count")).orderBy("Hour")
hourly.write.mode("overwrite").parquet("/app/data/hourly_analysis.parquet")

# 2. Status summary
status_count = df.groupBy("Status").agg(count("*").alias("Count"))
status_count.write.mode("overwrite").parquet("/app/data/status_summary.parquet")

# 3. Session type breakdown
session_analysis = df.groupBy("Session_Type", "Status") \
    .agg(count("*").alias("Count")) \
    .orderBy("Session_Type")
session_analysis.write.mode("overwrite").parquet("/app/data/session_analysis.parquet")

# 4. Archetype comparison
archetype_analysis = df.groupBy("Archetype", "Status") \
    .agg(count("*").alias("Count")) \
    .orderBy("Archetype")
archetype_analysis.write.mode("overwrite").parquet("/app/data/archetype_analysis.parquet")

print("All parquet files saved!")
spark.stop()